# run queue, e.g. start / shutdown / balance
import zmq

import threading
import logging
import time

from threading import Thread
from Queue import Queue

from upscale.master import balancer
from upscale.utils.rpc import RemoteClient
from upscale.utils.decorators import periodic_task

class Tasks(RemoteClient):
	pass

class Worker(RemoteClient):
	pass

def enqueue(func, *args, **kwargs):
	q.put((func, args, kwargs))

@periodic_task(interval=60)
def balance():
	def wrapper():
		balancer.rebalance()
		reload_all()

	enqueue(wrapper)

# reconfigure haproxy
def reload_all():
	from upscale.utils.common import get_hosts 
	for host in get_hosts():
		print ("Reloading host {0}.".format(host.private_dns_name))
		with Tasks("tcp://{0}:10000/".format(host.private_dns_name)) as h:
			# should run async and wait for all results to finish
			h.reload()

# start host
def start(host, namespace, website):
	# start container on min host
	# check minhost
	with Worker("tcp://{0}:10000/".format(host)) as h:
		#h.start(namespace, application).get(timeout=5)
		print ('Starting new container')
		h.start(namespace, website)

	enqueue(reload_all)

def destroy(namespace, website):
	# get all containers for project and destroy them
	pass

def upgrade(namespace, website):
	# rolling upgrade, first start new instances with new version,
	# then shutdown old ones
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

def main():
	""" New operations are pushed to master and queued for operation. """
	context = zmq.Context()
	socket = context.socket(zmq.PULL)
	socket.bind('tcp://127.0.0.1:5867')

	# listen for request
	while True:
		(func, args, kwargs) = socket.recv_pyobj()
		print func
		enqueue(func, *args, **kwargs)

	socket.close()

q = Queue()

t = Thread(target=worker)
t.daemon = True
t.start()

if __name__ == '__main__':
	main()	


