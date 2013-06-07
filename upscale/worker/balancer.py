import os

from kombu.common import Broadcast
from celery import Celery
from celery.contrib.methods import task

from upscale import celeryconfig

celery = Celery()
celery.config_from_object(celeryconfig)

@celery.task(name='balancer.rebalance')
def rebalance():
	print 'Balancing'

	containers={}
	for i in get_instances():
		a=get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
		containers[i.id] = a.get()

	pprint.pprint(containers)

	# use weighted rebalance
	# these are servers which shouldnt be target
	blacklist = []

	# also weighted hosts, so one in static host, one on spot instance
	min_host = None
	max_host = None
	for host in containers:
		if (not min_host or len(containers[host])<len(containers[min_host])):
			min_host=host
			pass
		if (not max_host or len(containers[host])>len(containers[max_host])):
			max_host=host
			pass
	print min_host
	print max_host

	# pop removes
	if (min_host == max_host):
		raise Exception("Nothing to do")
	
	# find container that is not on new host
	# this doesn't work, because it sets on _id should on project_applicatoin
	container = (set(containers[max_host]) - set(containers[min_host])).pop()


	# add weighted moves
	print container	
	a = set(containers[max_host])
	a.remove(container)
	b = set(containers[min_host])
	b.add(container)
	if (len(b) > len(a)):
		raise Exception("Already balanced")
		
	print 'Moving container {0} from host {1} to host {2}'.format(container, max_host, min_host)
	(namespace, application, id) = container.split('_')

	from celery import subtask, chain

	chain = subtask('tasks.start', kwargs={'namespace':namespace, 'project':application, }, queue=min_host, routing_key=min_host, immutable=True )
	chain = chain | subtask('tasks.shutdown', kwargs={'name':container, }, queue=max_host, routing_key=max_host, immutable=True ) 
	s = chain.apply_async()
	s.get()

	# after this start balance again, till nothing more to do


