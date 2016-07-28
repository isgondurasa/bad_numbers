import os
import json
import shutil
import asyncio
import tarfile
import paramiko
import settings

import logging

from aiopg.sa import create_engine

from datetime import datetime, timezone

from dateutil.parser import parse as date_parse
from dateutil.relativedelta import *

from concurrent.futures import ProcessPoolExecutor

from sqlalchemy import select, join

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
    raw_cmd = 'find {} -name "2016-07-26.tar.bz2" -o -name "*.log"'.format(settings.CDR_SOURCE_FOLDER)
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
        "phone_num": line[49],
        "dnis": line[81],
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
        await add_frames(grouped_dnis)
        await add_calls(frames)
    return frames

async def _get_engine():
        engine = await create_engine(**settings.DB_CONNECTION)
        return engine

async def add_frames(frames):
    logger.info("add statistics for %d frames" % len(frames))
    engine = await _get_engine()

    async with engine.acquire() as conn:
        for dnis, frames in frames.items():
            val = {}
            val["dnis"] = dnis
            for frame in frames:
                if frame.get("status") in ("200", "503", "486", "487", "402", "480"):
                    val["code_%s" % frame.get("status")] = True
                else:
                    try:
                        if frame.get("status", None) and frame.get("status")[0] == "4":
                            val["code_other_4xx"] = True
                        elif frame.get("status", None) and frame.get("status")[0] == "5":
                            val["code_other_5xx"] = True
                    except Exception as e:
                        logger.exception(e)
                        print(frame)
                        print(val)
                connection_date = frame.get("connection_date", None)
                if connection_date:
                    val["last_connect_on"] = datetime.fromtimestamp(float(str(connection_date[:10])),
                                                                    timezone.utc)

            print(dnis)
            fields = [Statistics.c.id]
            result = await conn.execute(select(fields).where(Statistics.c.dnis == "0"))
            result = [r[0] for r in result]
            if not result:
                await conn.execute(Statistics.insert().values(**val))
            else:
                await conn.execute(Statistics.update()
                                   .where(Statistics.c.dnis ==str(dnis))
                                   .values(**val))

        return True


async def add_calls(frames):
    logger.info("add calls for %d frames" % len(frames))
    engine = await _get_engine()
    async with engine.acquire() as conn:
        for frame in frames:
            await conn.execute(Calls.insert().values(call_id=frame["call_id"],
                                                     dnis=frame["dnis"],
                                                     ani=frame["phone_num"],
                                                     duration=frame["duration"],
                                                     ring_time=frame.get("ring_time", 0),
                                                     non_zero=not frame["failed"],
                                                     time=frame["time"],
                                                     busy=frame["busy"],
                                                     failed=frame["failed"]))


async def add_dnis(frames):

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

    # logger.info("search on host: %s" % host)
    # yesterday_template = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
    # for filename in scp_target_file(host, yesterday_template):
    #     file_path = os.path.join(settings.LOCAL_FILE_FOLDER, filename)
    #     if not i:
    #         file_path = os.path.join(settings.LOCAL_FILE_FOLDER, filename)
    #     logger.info("got file: {}".format(file_path))
    #     frames = await process_file(file_path)
    #     try:
    #         if os.path.isfile(file_path):
    #             os.unlink(file_path)
    #     except Exception as e:
    #         print(e)
    #     return frames


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
