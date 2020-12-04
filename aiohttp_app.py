import asyncio
from uuid import uuid4
from aiohttp import web
from aioredis import create_redis_pool, Redis


routes = web.RouteTableDef()


async def get_redis_pool() -> Redis:
    redis_store = await create_redis_pool("redis://localhost:16379/0?encoding=utf-8")
    return redis_store


async def on_startup(app):
    app.redis_store = await get_redis_pool()


async def on_shutdown(app):
    await app.redis_store.close()


@routes.get('/ping')
async def ping(request):
    uuid = uuid4().hex

    await app.redis_store.set('uuid', uuid)
    _uuid = await app.redis_store.get('uuid')

    data = dict(uuid=_uuid)

    return web.json_response(data)


app = web.Application()
app.add_routes(routes)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)


if __name__ == "__main__":
    web.run_app(app, port=8000)

# python aiohttp_app
