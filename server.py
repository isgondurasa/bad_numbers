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


    async def base_get_entries(self, model, term, params):

        engine = await self._get_engine()
        async with engine.acquire() as conn:

            start_time = params.get("start_time", None)
            if not start_time:
                start_time = datetime.utcnow().strftime("%Y-%m-%d")

            end_time = params.get("end_time", None)
            if not end_time:
                end_time = datetime.utcnow().strftime("%Y-%m-%d")

            query = select([getattr(model.c, term),])

            if start_time and end_time:
                query = query.where(and_(model.c.date >= start_time,
                                         model.c.date <= end_time))

            min_attempt = params.get("min_attempt", None)
            if min_attempt:
                query = query.where(model.c.total_ingress >= min_attempt)

            min_succ_percent = params.get("min_success_percent", None)
            if min_succ_percent:
                query = query.where(model.c.valid_ingress/model.c.total_ingress*100 >= min_succ_percent)

            max_succ_percent = params.get("max_success_percent", None)
            if max_succ_percent:
                query = query.where(model.c.valid_ingress/model.c.total_ingress*100 <= max_succ_percent)

            code_200 = params.get("code_200", None)
            if code_200:
                query = query.where(model.c.code_200 / model.c.total_ingress*100 <= code_200)

            ip = params.get("ip", None)
            if ip:
                query = query.where(model.c.ip == ip)

            code_404 = params.get("code_404", None)
            if code_404:
                query = query.where(model.c.code_404 / model.c.total_ingress*100 >= code_404)

            code_503 = params.get("code_503", None)
            if code_503:
                query = query.where(model.c.code_503 / model.c.total_ingress*100 >= code_503)

            code_480 = params.get("code_480", None)
            if code_480:
                query = query.where(model.c.code_480 / model.c.total_ingress*100 >= code_480)

            code_486 = params.get("code_486", None)
            if code_486:
                query = query.where(model.c.code_486 / model.c.total_ingress*100 >= code_486)

            code_487 = params.get("code_487", None)
            if code_487:
                query = query.where(model.c.code_487 / model.c.total_ingress*100 >= code_487)

            code_4xx = params.get("code_4xx", None)
            if code_4xx:
                query = query.where(model.c.code_4xx / model.c.total_ingress*100 >= code_4xx)

            code_5xx = params.get("code_5xx", None)
            if code_5xx:
                query = query.where(model.c.code_5xx / model.c.total_ingress*100 >= code_5xx)

            result = await conn.execute(query)
            rows = [self.__parse_result_row(row) for row in await result.fetchall()]
            return rows




    async def GetANI(self, params):
        """
        GetANI( start time, end time, min attempt, min_succ_percent, max_succ_percent)
        """

        result = await self.base_get_entries(AniStatistics, "ani", params)
        self.write(json.dumps(result))




        # start_time = params.get("start_time", None)
        # if not start_time:
        #     start_time = datetime.utcnow().strftime("%Y-%m-%d")

        # end_time = params.get("end_time", None)
        # if not end_time:
        #     end_time = datetime.utcnow().strftime("%Y-%m-%d")

        # min_attempt = params.get("min_attempt", None)
        # min_succ_percent = params.get("min_success_percent", None)
        # max_succ_percent = params.get("max_success_percent", None)

        # engine = await self._get_engine()
        # async with engine.acquire() as conn:
        #     # no need to aggregate, because data is already aggregated
        #     model = AniStatistics
        #     query = select([model.c.ani,])

        #     if start_time and end_time:
        #         query = query.where(and_(model.c.date >= start_time,
        #                                  model.c.date <= end_time))

        #     if end_time:
        #         query = query.where(model.c.date <= end_time)

        #     if min_attempt:
        #         query = query.where(model.c.total_ingress >= min_attempt)

        #     if min_succ_percent:
        #         query = query.where(model.c.valid_ingress/model.c.total_ingress*100 >= min_succ_percent)

        #     if max_succ_percent:
        #         query = query.where(model.c.valid_ingress/model.c.total_ingress*100 <= max_succ_percent)

        #     #  TODO (aos): have to handler min/max succ percent
        #     result = await conn.execute(query)
        #     rows = [self.__parse_result_row(row) for row in await result.fetchall()]
        #     #grouped = self.__group_by_term("ani", rows)
        #     self.write(json.dumps(rows))

    async def GetDNIS(self, params):
        result = await self.base_get_entries(DnisStatistics, "dnis", params)
        self.write(json.dumps(result))

        # start_time = params.get("start_time", None)
        # if not start_time:
        #     start_time = datetime.utcnow().strftime("%Y-%m-%d")

        # end_time = params.get("end_time", None)
        # if not end_time:
        #     end_time = datetime.utcnow().strftime("%Y-%m-%d")

        # min_attempt = params.get("min_attempt", None)
        # min_succ_percent = params.get("min_success_percent", None)
        # max_succ_percent = params.get("max_success_percent", None)

        # engine = await self._get_engine()
        # async with engine.acquire() as conn:
        #     # no need to aggregate, because data is already aggregated
        #     model = DnisStatistics
        #     query = select([model.c.ani,])

        #     if start_time and end_time:
        #         query = query.where(and_(model.c.date >= start_time,
        #                                  model.c.date <= end_time))

        #     if end_time:
        #         query = query.where(model.c.date <= end_time)

        #     if min_attempt:
        #         query = query.where(model.c.total_ingress >= min_attempt)

        #     if min_succ_percent:
        #         query = query.where(model.c.valid_ingress/model.c.total_ingress*100 >= min_succ_percent)

        #     if max_succ_percent:
        #         query = query.where(model.c.valid_ingress/model.c.total_ingress*100 <= max_succ_percent)

        #     #  TODO (aos): have to handler min/max succ percent
        #     result = await conn.execute(query)
        #     rows = [self.__parse_result_row(row) for row in await result.fetchall()]
        #     #grouped = self.__group_by_term("ani", rows)
        #     self.write(json.dumps(rows))


    async def _get_potential_bad(self, params, term):
        date = params.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
        engine = await self._get_engine()

        async with engine.acquire() as conn:

            model = DnisStatistics
            if term == "ani":
                model = AniStatistics

            fields = (getattr(model.c, term),)
            q_ = and_(and_(model.c.date == date, model.c.non_zero_call == 0), model.c.duration == 0)
            result = await conn.execute(select(fields).where(q_))

            rows = [self.__parse_result_row(row) for row in await result.fetchall()]
            #  grouped = self.__group_by_term(term, rows)
            #  bad =  self.__check(grouped)
            return rows

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
