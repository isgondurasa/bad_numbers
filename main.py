import os
import json
import tarfile
import settings

from dnis import DnisStatistics

from collections import defaultdict
from datetime import datetime
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import *


__all__ = ("GetAni", "GetDNIS", "GetPotentialBadANI", "GetPotentialBadDNIS")


def _extract_data(f):
    for line in f:
        yield line

def _extract_stream(bytestream):
    for line in bytestream:
        yield line

def dump_tmp(filename, data):
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

def process_file(filename, time_range=None):
    if not filename:
        raise Exception("File not found")
    
    phones = {}

    cur_file = None
    
    for tarfile, f_info in _extract_tar(filename):

        if cur_file != f_info.name:
            cur_file = f_info.name
            print(cur_file)

        if time_range:
            t_start, t_end = time_range
            if t_start != t_end:
                 if not int(t_start) <= int(f_info.name.split("/")[1]) <= int(t_end):
                     continue
             
        f = tarfile.extractfile(f_info)
        
        lines = (line for line in _extract_data(f)
        )
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
        return frames

def get_dnis_stats(calls):
    def make_output(line):
        keys = ("dnis", "attempt", "non_zero", "busy", "has_ring", "failed")
        return [line.get(k, False) for k in keys]
    return list(map(make_output, calls))


def get_ani_stats(calls):
    def make_output(line):
        keys = ("phone_num", "attempt", "non_zero", "busy", "has_ring", "failed")
        return [line.get(k, False) for k in keys]
    return list(map(make_output, calls))


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


def GetAni(start_time, end_time, min_attempt, min_succ_percent, max_succ_percent):
    if not end_time:
        end_time = start_time
    file_names, time_extr  = __get_file_names(start_time, end_time)
    full_frames = []
    for file_name in file_names:
        full_frames.extend(process_file(os.path.join(settings.CDR_SOURCE_FOLDER, file_name + ".tar.bz2"),
                           time_extr))
    return get_ani_stats(full_frames)
        
    
def GetDNIS(start_time, end_time, min_attempt, min_succ_percent, max_succ_percent):
    if not end_time:
        end_time = start_time
    file_names, time_extr  = __get_file_names(start_time, end_time)

    full_frames = []
    for file_name in file_names:      
        full_frames.extend(process_file(os.path.join(settings.CDR_SOURCE_FOLDER, file_name + ".tar.bz2"),
                           time_extr))
        
    dnis = get_dnis_stats(full_frames)
    return dnis


def GetPotentialBadANI(date):
    file_names, _  = __get_file_names(date)

    full_frames = []
    for file_name in file_names:
        full_frames.extend(process_file(os.path.join(settings.CDR_SOURCE_FOLDER, file_name + ".tar.bz2")))

    grouped_anis = __group_by_term("phone_num", full_frames)

    bad = set()
    for ani, calls in grouped_anis.items():
        measures = {
            "duration": 0,
            "status": [],
            "ring_tone": False,
            "valid": 0,
            "hits": len(calls)
         }
        for call in calls:
            measures["duration"] += float(call["duration"])
            measures["status"].append(call["status"])

            measures["ring_tone"] = any([measures["ring_tone"],
                                         bool(call["ring_time"])])
            if not call["failed"]:
                measures["valid"] += 1

        if float(measures["valid"]) / float(measures["hits"]) * 100 >= settings.BAD_NUMBER_THRESHOLD:
            continue

        if not float(measures["duration"]) or \
           "486" not in measures["status"] or \
           not measures["ring_tone"]:
            bad.add(ani)
    return list(bad)

   
def GetPotentialBadDNIS(date):
    return []

if __name__ == "__main__":
    # tests
    frames = GetAni("2016-06-26 0:00:00", "2016-06-27 1:00:00", 0, 60, 100)
    print(frames)

    frames = GetPotentialBadANI("2016-06-26")
    print (frames)
