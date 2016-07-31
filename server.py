import json
import aiopg
import asyncio
import settings

import logging

import tornado.platform.asyncio
from tornado.web import RequestHandler

from models import *
from settings import DB_CONNECTION

from aiopg.sa import create_engine
from sqlalchemy.sql import or_, and_
from sqlalchemy import select, join

from datetime import datetime
from collections import defaultdict

from sqlalchemy import func


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s %(levelname)s:%(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class BadCallApiHandler(RequestHandler):

    def __parse_result_row(self, row):
        return {el: row[el] for el in row}

    def __group_by_term(self, term, calls):
        res = defaultdict(list)
        for call in calls:
            res[call[term]].append(call)
        return res

    def __check(self, items):

        bad = set()
        for ani, calls in items.items():
            measures = {
                "duration": 0,
                "status": [],
                "ring_time": False,
                "valid": 0,
                "hits": len(calls)
            }

            for call in calls:
                measures["duration"] += float(call["duration"])
                measures["ring_time"] = any([measures["ring_time"],
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


    async def _get_engine(self):
        engine = await create_engine(**settings.DB_CONNECTION)
        return engine

    async def get(self, *args, **kwargs):
        method_name = kwargs.pop("method", None)
        method = getattr(self, method_name, None)

        arguments = {k: v[0].decode("utf-8") for k, v in self.request.arguments.items()}

        if method:
            return await method(arguments)

    async def GetANI(self, params):
        """
        GetANI( start time, end time, min attempt, min_succ_percent, max_succ_percent)
        """
        start_time = params.get("start_time", None)
        if not start_time:
            start_time = datetime.utcnow().strftime("%Y-%m-%d")

        end_time = params.get("end_time", None)
        if not end_time:
            end_time = datetime.utcnow().strftime("%Y-%m-%d")

        min_attempt = params.get("min_attempt", None)
        min_succ_percent = params.get("min_succ_percent", None)
        max_succ_percent = params.get("max_succ_percent", None)

        engine = await self._get_engine()
        async with engine.acquire() as conn:
            # no need to aggregate, because data is already aggregated
            query = select(Calls.c)

            if start_time:
                query = query.where(Calls.c.time >= start_time)

            if end_time:
                query = query.where(Calls.c.time <= end_time)

            if min_attempt:
                query = query.where(Calls.c.num_valid_egress >= min_attempt)

            #  TODO (aos): have to handler min/max succ percent
            result = await conn.execute(query)
            rows = [self.__parse_result_row(row) for row in await result.fetchall()]
            grouped = self.__group_by_term("ani", rows)
            self.write(json.dumps(grouped))

    async def GetDNIS(self, params):
        engine = await self._get_engine()
        with engine.acquire() as conn:
            pass

    async def _get_potential_bad(self, params, term):
        date = params.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        date_start = date + ' 00:00:00'
        date_end = date + ' 23:59:59'
        engine = await self._get_engine()
        async with engine.acquire() as conn:
            fields = (Calls.c.ani, Calls.c. dnis, Calls.c.non_zero, Calls.c.duration, Calls.c.busy, Calls.c.ring_time, Calls.c.failed)
            result = await conn.execute(select(fields).where(and_(Calls.c.time >= date_start,
                                                                  Calls.c.time <= date_end)))
            rows = [self.__parse_result_row(row) for row in await result.fetchall()]
            grouped = self.__group_by_term(term, rows)
            bad =  self.__check(grouped)
            return bad

    async def GetPotentialBadANI(self, params):
        result = await self._get_potential_bad(params, "ani")
        self.write(json.dumps(result))

    async def GetPotentialBadDNIS(self, params):
        result = await self._get_potential_bad(params, "dnis")
        self.write(json.dumps(result))

def make_server():
    return tornado.web.Application([
        (r'^/api/(?P<method>\w+?)$', BadCallApiHandler, {}, 'bad_number_api'),
    ], debug=settings.DEBUG, reload=True)

if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    api = make_server()
    api.listen(settings.PORT)
    asyncio.get_event_loop().run_forever()
