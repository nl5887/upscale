import os
import socket
import datetime 
import pprint

from kombu.common import Broadcast
from celery import Celery

from upscale import celeryconfig

from upscale.config import config
from upscale.db.model import Session, Namespace, Domain, Project, Template
from upscale.utils import lxc

from celery import Celery

celery = Celery()
celery.config_from_object(celeryconfig)

if __name__ == '__main__':
    celery.worker_main()

