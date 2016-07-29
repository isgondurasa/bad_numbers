import os
import json
import shutil
import asyncio
import tarfile
import paramiko
import settings

import logging

from aiopg.sa import create_engine

from datetime import datetime, timedelta, timezone

from dateutil.parser import parse as date_parse
from dateutil.relativedelta import *

from concurrent.futures import ProcessPoolExecutor

from sqlalchemy import select, join, and_

from collections import defaultdict

from models import *


# set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s %(levelname)s:%(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def scp_target_file(host, template=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,
                username=settings.USERNAME,
                password=settings.PASSWORD)
    raw_cmd = 'find {} -name "2016-06-26.tar.bz2" -o -name "*.log"'.format(settings.CDR_SOURCE_FOLDER)
    stdin, stdout, stderr = ssh.exec_command(raw_cmd)
    file_list = stdout.read().splitlines()

    ftp = ssh.open_sftp()
    filenames = []
    for index, f_ in enumerate(file_list):
        _, filename = os.path.split(f_)
        filename = filename.decode("utf-8")
        logger.info("find file %s" % filename)
        f_name = "{}_{}".format(index, filename)
        ftp.get(f_.decode("utf-8"),
                os.path.join(settings.LOCAL_FILE_FOLDER,
                f_name))
        yield f_name


def _extract_data(f):
    for line in f:
        yield line


def _extract_stream(bytestream):
    for line in bytestream:
        yield line


def _dump_tmp(filename, data):
    with open(filename, "w") as out:
        r = {}
        for k, v in data.items():
            r[k] = v.to_json()
        out.write(json.dumps(r))


def _extract_tar(filename):
    tar = tarfile.open(filename)
    for t_info in tar:
        if ".cdr" in t_info.name:
            yield tar, t_info


def _extract_multiple_data(line):
    line = line.decode("utf-8").split("?")
    dump = {
        "phone_num": line[12],
        "dnis": line[49],
        "lrn_dis": line[80],
        "status": line[7][:3] if line [7] != "NULL" else None,
        "duration": float(line[50]),
        "pdd": line[51],
        "call_id": line[1],
        "ring_time": line[52],
        "busy": True if "USER_BUSY" in line[-1] else False
    }

    if dump.get('status', None) and dump["status"] in settings.UNBLOCK_CODES:
        dump["connection_date"] = line[3]

    dump['time'] = datetime.fromtimestamp(float(str(line[3][:10])),
                                          timezone.utc)

    return dump


def __group_by_term(term, calls):
    res = defaultdict(list)
    for call in calls:
        res[call[term]].append(call)
    return res


def __daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + relativedelta(n)


def __get_time_range(start_dt, end_dt):
    return start_dt.hour, end_dt.hour,


def __get_file_names(start_dt, end_dt=None):

    if not end_dt:
        start_dt = date_parse(start_dt)
        return [start_dt.strftime("%Y-%m-%d")], __get_time_range(start_dt, start_dt)

    start_dt = date_parse(start_dt)
    end_dt = date_parse(end_dt)

    dates = __daterange(start_dt, end_dt)
    time_tuple = __get_time_range(start_dt, end_dt)

    return [d.strftime("%Y-%m-%d") for d in dates], time_tuple


async def _get_engine(self):
    dsn = settings.DB_CONNECTION
    engine = await create_engine(user=dsn.get('user'),
                                 database=dsn.get('database'),
                                 host=dsn.get('host'),
                                 password=dsn.get('password'))
    return engine

async def process_file(filename):
    if not filename:
        raise Exception("File not found")

    cur_file = None
    for tarfile, f_info in _extract_tar(filename):

        if cur_file != f_info.name:
            cur_file = f_info.name
            print(cur_file)

        f = tarfile.extractfile(f_info)
        lines = (line for line in _extract_data(f))
        frames = []
        for line in lines:
            _line = _extract_multiple_data(line)
            # call_info = {k:v for k,v in _line}

            def is_good_call(call):
                if call["duration"] and call["duration"] != "0":
                    return True

                return bool(call["status"] not in ["487", "402"] and
                            int(call["pdd"]) > 500)

            _line["failed"] = not is_good_call(_line)
            frames.append(_line)

        grouped_dnis = await add_dnis(frames)
        await add_statistics(grouped_dnis)
        await add_calls(frames)
    return frames

async def _get_engine():
        engine = await create_engine(**settings.DB_CONNECTION)
        return engine

STATUSES = ("200", "503", "486", "487", "402", "480")

def increase_value(frame, val):
    if frame.get("status") in STATUSES:
        stat = "code_%s" % frame.get("status")
        stat_count = val.get(stat, 0)
        val[stat] = stat_count + 1
    else:
        if frame.get("status", None) and frame.get("status")[0] == "4":
            v =  val.get("code_other_4xx", 0)
            val["code_other_4xx"] = v + 1
        elif frame.get("status", None) and frame.get("status")[0] == "5":
            v =  val.get("code_other_5xx", 0)
            val["code_other_5xx"] = v + 1
    return val
    

async def add_statistics(frames):
    """
    adds/updates statistics and counts statuses
    """
    logger.info("add statistics for %d frames" % len(frames))
    engine = await _get_engine()

    async with engine.acquire() as conn:
        for dnis, frames in frames.items():
            val = dict(dnis=dnis,)
            for frame in frames:
                val = increase_value(frame, val)
                connection_date = frame.get("connection_date", None)
                if connection_date:
                    val["date"] = datetime.fromtimestamp(float(str(connection_date[:10])),
                                                         timezone.utc)

            fields = [Statistics.c,]
            result = await conn.execute(select(Statistics.c).where(Statistics.c.dnis == dnis))
            result = [r for r in result]
            
            if result:
                for k, v in val.items():
                    if "code" in k: ###
                        if val.get(k, None):
                            val[k] = int(val[k]) + int(getattr(result, k, 0))
                        else:
                            val[k] = getattr(result, k)

                await conn.execute(Statistics.update()
                                   .where(Statistics.c.dnis ==str(dnis))
                                   .values(**val))

            if not result:
                await conn.execute(Statistics.insert().values(**val))
            
                
        return True


async def add_calls(frames):
    """
    add new call row to database, if there is no such pair:
    dnis and ani.
    if there is such pair -> do update
    """

    def group_by(frames):
        terms = defaultdict(list)

        for frame in frames:
            terms["{}_{}".format(frame["dnis"],
                                 frame["phone_num"])].append(frame)
        grouped_terms = {}
        for term, mini_frames in terms.items():
            res = {}
            for m_fr in mini_frames:
                if not res:
                    res = m_fr
                    res["ani"] = m_fr["phone_num"]
                    res.pop("lrn_dis")
                    res.pop("pdd")
                    res.pop("status")
                    res.pop("phone_num")
                    print(res)
                    res.pop("connection_date", None)
                    continue
                res["call_id"] = m_fr["call_id"]
                res["failed"] = m_fr["failed"]
                if not res["failed"]:
                    egr_count = res.get("num_valid_egress", 0)
                    res["num_valid_egress"] = egr_count + 1
                res["ring_time"] = res.get("ring_time", 0) + m_fr.get("ring_time", 0)
                res["time"] = m_fr["time"]
                res["busy"] = m_fr["busy"]
                res["duration"] = res.get("duration", 0) + m_fr.get("duration", 0)

            grouped_terms[term] = res

        return grouped_terms

    
    logger.info("add calls for %d frames" % len(frames))
    engine = await _get_engine()
    async with engine.acquire() as conn:

        grouped_frames = group_by(frames)

        for term, val in grouped_frames.items():
            dnis, ani = term.split("_")
            result = await conn.execute(select(Calls.c).where(and_(Calls.c.ani == ani,
                                                                   Calls.c.dnis == dnis)))
            result = [r for r in result]
            if result:
                try:
                    await conn.execute(Calls.update().where(and_(Calls.c.ani == ani,
                                                                 Calls.c.dnis == dnis))
                                                     .values(**val))

                except Exception as e:
                    
                    print(str(e))

            else:
                await conn.execute(Calls.insert().values(**val))
    return True


async def add_dnis(frames):
    """
    add new dns row to database, if there is no such dnis in database
    """
    def __diff(l1, l2):
        l1 = set(l1)
        l2 = set(l2)
        return list(l1.difference(l2))

    logger.info("add dnis")
    engine = await _get_engine()

    dnis = __group_by_term("dnis", frames)
    dnis_nums = list(dnis.keys())

    async with engine.acquire() as conn:
        result = await conn.execute(select([Dnis.c.dnis]).where(Dnis.c.dnis.in_(dnis_nums)))
        result = [r[0] for r in result]
        dnis_to_insert = __diff(dnis_nums, result)

        for dnis_ in dnis_to_insert:
            await conn.execute(Dnis.insert().values(dnis=dnis_,
                                                    is_mobile=True,
                                                    carrier="Any text"))

        return dnis

async def get_file(host):
    file_path = os.path.join(settings.LOCAL_FILE_FOLDER, "0_2016-07-26.tar.bz2")
    return await process_file(file_path)

    logger.info("search on host: %s" % host)
    yesterday_template = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
    for filename in scp_target_file(host, yesterday_template):
        file_path = os.path.join(settings.LOCAL_FILE_FOLDER, filename)
        file_path = os.path.join(settings.LOCAL_FILE_FOLDER, filename)
        logger.info("got file: {}".format(file_path))
        frames = await process_file(file_path)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
        return frames


def enable_process(host):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_file(host))
    return loop

if __name__ == "__main__":
    logger.info("Start CDR Bad NUmbers")
    print("Start CDR Bad NUmbers")
    loops = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        for loop in executor.map(enable_process, settings.CDR_SERVICE_HOSTS):
            loops.append(loop)
