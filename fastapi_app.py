from aioredis import create_redis_pool, Redis

from uuid import uuid4
from fastapi import FastAPI


app = FastAPI()


async def get_redis_pool() -> Redis:
    redis_store = await create_redis_pool("redis://localhost:16379/0?encoding=utf-8")
    return redis_store


@app.on_event('startup')
async def startup_event():
    app.redis_store = await get_redis_pool()


@app.on_event('shutdown')
async def shutdown_event():
    await app.redis_store.close()


@app.get('/ping')
async def ping():
    uuid = uuid4().hex

    await app.redis_store.set('uuid', uuid)
    _uuid = await app.redis_store.get('uuid')

    return dict(uuid=_uuid)


# uvloop fastapi:app
# gunicorn -w 1 -k uvicorn.workers.UvicornWorker runserver:app -b 127.0.0.1:8000
