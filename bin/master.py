# run queue, e.g. start / shutdown / balance
import zmq

import threading
import logging
import time
import sys
import os

from threading import Thread
from Queue import Queue

POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))

if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'upscale', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from upscale.master import balancer
from upscale.utils.rpc import RemoteClient
from upscale.utils.decorators import periodic_task

class Tasks(RemoteClient):
	pass

class Worker(RemoteClient):
	pass

def enqueue(func, *args, **kwargs):
	q.put((func, args, kwargs))

class Service(object):
	@periodic_task(interval=300)
	def _balance(self):
		def wrapper():
			balancer.rebalance()
			self.reload_all()

		enqueue(wrapper)

	# reconfigure haproxy
	def reload_all(self):
		from upscale.utils.common import get_hosts 
		for host in get_hosts():
			print ("Reloading host {0}.".format(host.private_dns_name))
			with Tasks("tcp://{0}:10000/".format(host.private_dns_name)) as h:
				# should run async and wait for all results to finish
				h.reload()

	# start host
	def start(self, namespace, application):
		from upscale.master.balancer import get_containers
		def wrapper():	
			print namespace, application,
			(hosts, containers) = get_containers()

			# also weighted hosts, so one in static host, one on spot instance
			min_host = None
			for host in containers:
				if (not min_host or len(containers[host])<len(containers[min_host])):
					# check if it already contains project
					min_host_applications = set([(b.split('_')[0], b.split('_')[1]) for b in containers[host] if len(b.split('_'))==3])
					if ((namespace, application) in min_host_applications):
						continue

					min_host=host

			if not min_host:
				raise Exception('No host available')

			print 'Starting on host {0}.'.format(min_host)
			# start container on min host
			# check minhost
			with Worker("tcp://{0}:10000/".format(hosts[min_host])) as h:
				#h.start(namespace, application).get(timeout=5)
				print ('Starting new container')
				h.start(namespace, application)

			self.reload_all()

		enqueue(wrapper, )

	def destroy(self, namespace, website):
		# get all containers for project and destroy them
		def wrapper():
			print namespace, application,
			(hosts, containers) = get_containers()
			for host in containers:
				for container in containers[host]:
					pass
		pass

	def upgrade(self, namespace, website):
		# rolling upgrade, first start new instances with new version,
		# then shutdown old ones
		
		# get containers and host of old version
		# start new containers with new version
		# shutdown old versions
		pass

def worker():
    """ Worker runs a queue of operations on the upscale cluster. """
    while True:
	(func, args, kwargs) = q.get()
	print func 
	try:
		func(*args, **kwargs)
	except Exception, e:
		print e
		logging.exception('Worker')

from upscale.utils.rpc import Server

import time
import sys
import traceback

from upscale.worker.worker import Worker

q = Queue()

t = Thread(target=worker)
t.daemon = True
t.start()

if __name__ == '__main__':
        from upscale.worker import tasks
        with Server("tcp://0.0.0.0:5867", {'Service': Service()}) as s:
                s.run()

