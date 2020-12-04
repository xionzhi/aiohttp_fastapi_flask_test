#### 测试版本

```
Python 3.7.4

Flask==1.0.2
aiohttp==3.6.2
fastapi==0.61.1

redis==3.3.4
aioredis==1.3.1
```

#### 测试工具

```
wrk -t8 -c200 -d10s --latency "http://127.0.0.1:8000/ping"
```

#### 测试结果

```
# aiohttp
Running 10s test @ http://127.0.0.1:8000/ping
  8 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   201.97ms  176.09ms   1.12s    92.14%
    Req/Sec   159.55     63.28   252.00     61.39%
  Latency Distribution
     50%  154.53ms
     75%  167.49ms
     90%  206.97ms
     99%    1.10s 
  11721 requests in 10.07s, 2.25MB read
  Socket errors: connect 0, read 58, write 0, timeout 0
Requests/sec:   1164.27
Transfer/sec:    228.53KB


# fastapi
Running 10s test @ http://127.0.0.1:8000/ping
  8 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   111.16ms   11.88ms 163.06ms   66.61%
    Req/Sec   225.05     31.60   310.00     75.72%
  Latency Distribution
     50%  110.91ms
     75%  117.71ms
     90%  126.57ms
     99%  144.82ms
  17937 requests in 10.04s, 2.87MB read
  Socket errors: connect 0, read 71, write 0, timeout 0
Requests/sec:   1785.86
Transfer/sec:    292.99KB


# flask
Running 10s test @ http://127.0.0.1:8000/ping
  8 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   811.56ms  136.84ms 896.49ms   93.21%
    Req/Sec    21.51     13.47    70.00     75.90%
  Latency Distribution
     50%  843.81ms
     75%  855.54ms
     90%  867.01ms
     99%  888.28ms
  1518 requests in 10.09s, 290.55KB read
  Socket errors: connect 0, read 325, write 38, timeout 0
Requests/sec:    150.43
Transfer/sec:     28.79KB
```

#### 源代码 [github]()

**1. aiohttp**

```python
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
```

**2. fastapi**

```python
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
```

**2. flask**

```python
import redis

from uuid import uuid4
from flask import Flask, jsonify


app = Flask(__name__)

pool = redis.ConnectionPool(host='localhost', port=16379, db=0, decode_responses=True)  
redis_store = redis.Redis(connection_pool=pool)


@app.route('/ping')
def ping():
    uuid = uuid4().hex

    redis_store.set('uuid', uuid)
    _uuid = redis_store.get('uuid')

    return jsonify(dict(uuid=_uuid))


if __name__ == '__main__':
    app.run(port=8000)


# gunicorn flask_app:app
```

