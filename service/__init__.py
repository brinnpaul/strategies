import os
import json
import boto3
import logging
import rediscluster

from flask import Flask
from celery import Celery
from rediscluster import StrictRedisCluster

app = Flask(__name__, static_folder='templates/static', static_url_path='/static')

app.config.from_object('config_local.Config')

os.environ['USERNAME_NEXUSADSPY'] = app.config['APPNEXUS_USERNAME']
os.environ['PASSWORD_NEXUSADSPY'] = app.config['APPNEXUS_PASSWORD']

if app.config['DEBUG'] is True:
    import redis
    _redis_host = app.config['REDIS_HOST_LOCAL']
    _redis_port = app.config['REDIS_PORT_LOCAL']
    redis_store = redis.StrictRedis(host=_redis_host,
                                    port=_redis_port,
                                    db=0)
else:
    _redis_host = app.config['REDIS_HOST']
    _redis_port = app.config['REDIS_PORT']
    redis_store = StrictRedisCluster(host=_redis_host,
                                     port=_redis_port,
                                     decode_responses=True)


if not app.config['KEEP_REDIS_STORE']:
    redis_store.set('campaigns', {})

def make_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

from service import views
from service import tasks
from service import strategies