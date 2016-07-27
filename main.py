import os
import json
import tarfile

import asyncio
from aiopg.sa import create_engine
import settings

from datetime import datetime
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import *

from collections import defaultdict

from models import *

__all__ = ("GetAni", "GetDNIS", "GetPotentialBadANI", "GetPotentialBadDNIS")


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
        "dnis": line[12],
        "status": line[7][:3] if line [7] != "NULL" else None,
        "duration": float(line[50]),
        "pdd": line[51],
        "call_id": line[1],
        "ring_time": line[52]
    }

    if dump.get('status', None) and dump["status"] in settings.UNBLOCK_CODES:
        dump["connection_date"] = line[3]
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

        await add_frames(frames)
        await add_calls(frames)
        await add_dnis(frames)
    return frames

async def _get_engine():
        engine = await create_engine(**settings.DB_CONNECTION)
        return engine

async def add_frames(frames):
    print("add statistics for %d frames" % len(frames))

    engine = await _get_engine()
    async with engine.acquire() as conn:


        import ipdb; ipdb.set_trace()

        print(frame[0])
        for frame in frames:
            print(f)


        return True

async def add_calls(frames):
    pass

async def add_dnis(frames):
    pass


async def go():
    filename = "2016-06-26.tar.bz2"
    filepath = os.path.join(settings.CDR_SOURCE_FOLDER, filename)
    frames = await process_file(filepath)


loop = asyncio.get_event_loop()
loop.run_until_complete(go())


