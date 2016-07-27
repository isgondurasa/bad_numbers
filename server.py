import json
import aiopg
import asyncio
import settings

import logging

import tornado.platform.asyncio
from tornado.web import RequestHandler

from settings import DB_CONNECTION


async def _get_engine():
        engine = await create_engine(**settings.DB_CONNECTION)
        return engine


class BadCallApiHandler(RequestHandler):
    async def get(self, *args, **kwargs):
        method_name = kwargs.get("method", None)
        method = getattr(self, method_name, None)
        if method:
            return await method(*args, **kwargs)


    async def GetAni(self, params):
        pass

    async def GetDNIS(self, params):
        pass

    async def GetPotentialBadANI(self, params):
        pass

    async def GetPotentialBadDNIS(self, params):
        pass



def make_server():
    return tornado.web.Application([
        (r'^/api/(?P<method>\w+?)$', BadCallApiHandler, {}, 'bad_number_api'),
    ])



if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    api = make_app()
    api.listen(settings.PORT)
    asyncio.get_event_loop().run_forever()
