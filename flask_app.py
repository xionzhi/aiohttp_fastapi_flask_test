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
