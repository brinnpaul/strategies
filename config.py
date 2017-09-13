class BaseConfig(object):
    DEBUG = False
    VERSION = '0.0.1'

    REDIS_HOST_LOCAL = '127.0.0.1'
    REDIS_PORT_LOCAL = 6379
    KEEP_REDIS_STORE = True
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
    CELERY_TASK_SERIALIZER='json'
    CELERY_ACCEPT_CONTENT=['json']

    APPNEXUS_MEMBER_ID=''
    APPNEXUS_PASSWORD=''
    APPNEXUS_USERNAME=''

    REDIS_HOST = ''
    REDIS_PORT = ''