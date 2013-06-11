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

@periodic_task(interval=300)
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
def start(namespace, application):
	from upscale.master.balancer import get_containers

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


