import os

import datetime
import logging

from upscale.utils.common import get_hosts 
from upscale.utils.rpc import RemoteClient

class Tasks(RemoteClient):
	pass

class Worker(RemoteClient):
	pass

def rebalance():
	print 'Balancing hosts'

	hosts = {}

	containers={}
	for host in get_hosts():
		p = []
		try:
			hosts[host.id]=host.private_dns_name
			print ("tcp://{0}:10000/".format(host.private_dns_name))
			with Worker("tcp://{0}:10000/".format(host.private_dns_name)) as h:
				#p.append(h.get_containers())
				#containers[host.id] = h.get_containers().get(timeout=5)
				containers[host.id] = h.get_containers()

			#gevent.joinall(p)
			#containers[host.id] = h.get_containers().get(timeout=5)
		except Exception, e:
			print e

	# use weighted rebalance
	# these are servers which shouldnt be target
	blacklist = []

	#while True:

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
	if (min_host == max_host):
		print 'Nothing to balance, already balanced.'
		return
	
	# find container that is not on new host
	old_container = None
	min_host_applications = set([(b.split('_')[0], b.split('_')[1]) for b in containers[min_host] if len(b.split('_'))==3])

	for container in containers[max_host]:
		if (len(container.split('_'))!=3):
			continue

		application = (container.split('_')[0], container.split('_')[1])	
		if not (application in min_host_applications):
			old_container = container
			break

	# add weighted moves

	if (len(containers[min_host]) + 1 > len(containers[max_host]) - 1):
		print 'Nothing to balance, already balanced.'
		return
		
	print 'Moving {0} from host {1} to host {2}'.format(container, max_host, min_host)

	(namespace, application, id) = container.split('_')

	# start container on new host
	with Worker("tcp://{0}:10000/".format(hosts[min_host])) as h:
		print ('Starting new container')
		#new_container = h.start(namespace, application)
		new_container = h.start(namespace, application)
		containers[min_host]=new_container

	# delete container on old host
	with Worker("tcp://{0}:10000/".format(hosts[max_host])) as h:
		print ('Destroying old container on old host')
		#h.shutdown(container).get()
		#h.wait(container, state='STOPPED').get()
		#h.destroy(container).get()
		h.shutdown(container)
		h.wait(container, state='STOPPED')
		h.destroy(container)
		containers[max_host].remove(container)

	print ('Successfully moved from old host to new host')
	
	return



