import os
import datetime 
import celery
import logging

from upscale import config
from upscale.worker import tasks

def shutdown(host_arg, name_arg):
	try:
		task = tasks.shutdown.apply_async(kwargs={'name': name_arg, }, queue=host_arg, routing_key=host_arg, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
		task.get(timeout=30)
	except celery.exceptions.TimeoutError, e:
		containers[i.id] = []
		logging.exception("Timeout occured while shutdown of container {0} for host {1}.".format(host_arg, name_arg))
	

def status():
	containers={}
        for i in tasks.get_instances():
		try:
			a=tasks.get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
			containers[i.id] = a.get(timeout=5)
		except celery.exceptions.TimeoutError, e:
			containers[i.id] = []
			logging.exception("Timeout occured while retrieving status for host {0}.".format(i.id))
		
	return (containers)

