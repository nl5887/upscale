from kombu.common import Broadcast
from kombu import Queue, Exchange

import upscale
from upscale import config

config=config.config

BROKER_URL = config['broker']['url'] 

CELERY_RESULT_BACKEND = config['broker']['url'] 
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True
CELERY_WORKER_DIRECT = True

# Additional settings
CELERY_IMPORTS = ("upscale.worker.tasks", 'upscale.worker.balancer' )

CELERY_CONFIG_MODULE = 'celeryconfig'

# get instance metadata for private queue
from boto.utils import get_instance_metadata
m = get_instance_metadata()

CELERY_QUEUES = (Broadcast('broadcast_tasks'), Queue('tasks',), Queue(m['instance-id'], Exchange(m['instance-id']), routing_key=m['instance-id']))

CELERY_ROUTES = {'tasks.reload': {'queue': 'broadcast_tasks'}, 'tasks.get_containers': { 'queue': m['instance-id'], 'routing_key': m['instance-id']}, 'tasks.start': { 'queue': m['instance-id'], 'routing_key': m['instance-id']}, 'tasks.shutdown': { 'queue': m['instance-id'], 'routing_key': m['instance-id']}, 'balancer.rebalance': {'queue': 'tasks'} }

CELERY_CREATE_MISSING_QUEUES = True

