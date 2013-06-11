import os
import socket
import run
import datetime 
import pprint

from kombu.common import Broadcast
from celery import Celery

import upscale

from upscale import celeryconfig
from upscale.config import config
from upscale.db.model import Session, Namespace, Domain, Project, Template
from upscale.utils import lxc
from upscale.utils.common import get_hosts

datadir = os.path.join(os.path.dirname(os.path.realpath(upscale.__file__)), 'data')

hosts=[]

class Worker(object):
	""" Various convenience methods to make things cooler. """

	def start(self, namespace, project):
		import gevent
		g=gevent.spawn(run.run(namespace, project))
		container=g.get()
		return (container)

	def wait(self, name, state='RUNNING'):
		print lxc.wait(name, state)	
		return (True)

	def destroy(self, name):
		print lxc.destroy(name)	
		return (True)

	def shutdown(self, name):
		print lxc.shutdown(name)	
		return (True)

	def get_containers(self):
		return (lxc.get_containers())
	
"""
def get_hosts():
	import boto.ec2

	access=config['ec2']['access-key']
	key= config['ec2']['secret-key'] 
	region= config['ec2']['region'] 
	vpc_id= config['ec2']['vpc-id'] 

	ec2_conn = boto.ec2.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=access)

	instances = []
	for reservation in ec2_conn.get_all_instances(filters={'vpc-id':vpc_id}):
		for instance in reservation.instances:
			instances.append(instance)
	
	return (instances)
"""
def get_applications():
	session = Session()

	hosts = []
	
	for host in get_hosts():
		hosts.append({'id': host.id + '_' + host.instance_type, 'ipaddr': host.private_ip_address})

	
	applications={}
	namespaces = session.query(Namespace).all()
	for namespace in namespaces:
		for project in namespace.projects:
			application={}
			application['id'] = ''.join(filter(lambda c: c.islower() or c.isdigit() or c=='-', namespace.name)) + '_' + ''.join(filter(lambda c: c.islower() or c.isdigit() or c=='-', project.name))
			application['domains']=[{'name':config['domain'].format(project.name, namespace.name), 'id': ''.join(filter(lambda c: c.islower() or c.isdigit() or c=='-', config['domain'].format(project.name, namespace.name)))},]
			for domain in project.domains:
				application['domains'].append ({'name':domain.name, 'id': ''.join(filter(lambda c: c.islower() or c.isdigit() or c=='-', domain.name))})
			application['containers']=[]
			application['hosts']=hosts
			applications[application['id']]=application
	return (applications)

#from boto.utils import get_instance_metadata
#m = get_instance_metadata()

def start1(namespace, project):
	# start container
        containers={}
        for i in get_instances():
                a=get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
                containers[i.id] = a.get()

        min_host = None
        for host in containers:
                if (not min_host or len(containers[host])<len(containers[min_host])):
                        min_host=host
                        pass

	# prevent running same container on min_host
	start.apply_async(kwargs={'namespace':namespace, 'project':project}, queue=min_host, routing_key=min_host, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), ).get()

	# start chained rebalance afterwards

def update():
	# run new instances
	# shutdown old instances
	# deployed!
	pass

def status():
	containers={}
        for i in get_instances():
                a=get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
                containers[i.id] = a.get(timeout=5)

        pprint.pprint(containers)


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
	return 'bla'
	
#@celery.task(name='tasks.get_containers', routing_key=m['instance-id'])
def start(namespace, project):
	container = run.run(namespace, project)
	return (container)

def destroy(name):
	print lxc.destroy(name)	
	return (True)

def shutdown(name):
	print lxc.shutdown(name)	
	return (True)
"""
def get_containers():
	return (lxc.get_containers())
	
@celery.task(name='tasks.balance', )
def balance():
	pass

"""
def reload():
	# reload applications
	applications = get_applications()

	for container in lxc.get_containers():
		try:
			ipaddr = socket.gethostbyname(container)
			(proj, appl, id) = container.split('_')
			applications[proj + '_' + appl]['containers'].append({'id': container, 'ipaddr': ipaddr})
			print ('added container ' + container + '('+ipaddr+') to ' + proj)
		except Exception as exc:
			print (exc)

		import jinja2
		templateLoader = jinja2.FileSystemLoader( searchpath="/" )
		templateEnv = jinja2.Environment( loader=templateLoader )
		from jinja2 import Template
		template = templateEnv.get_template(os.path.join(datadir, 'haproxy/haproxy.cfg.jinja2'))
		with open("/etc/haproxy/haproxy.cfg", "wb") as fh:
			fh.write (template.render(applications=applications, config=config))
		#print (template.render(applications=applications))

		template = templateEnv.get_template(os.path.join(datadir, 'haproxy/haproxy.global.cfg.jinja2'))
		with open("/etc/haproxy/haproxy.global.cfg", "wb") as fh:
			fh.write (template.render(applications=applications, config=config))

		import shlex, subprocess
	
		try:	
			pid = int(open('/var/run/haproxy.pid', 'r').read())
			os.kill(pid, 0)
			args = shlex.split('/bin/bash -c "haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -D -sf $(</var/run/haproxy.pid)"')
		except (IOError, OSError) as e:
			args = shlex.split('/bin/bash -c "haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -D"')
		finally:
			p = subprocess.Popen(args)
		
		try:	
			pid = int(open('/var/run/haproxy.global.pid', 'r').read())
			os.kill(pid, 0)
			args = shlex.split('/bin/bash -c "haproxy -f /etc/haproxy/haproxy.global.cfg -p /var/run/haproxy.global.pid -D -sf $(</var/run/haproxy.global.pid)"')
		except (IOError, OSError) as e:
			args = shlex.split('/bin/bash -c "haproxy -f /etc/haproxy/haproxy.global.cfg -p /var/run/haproxy.global.pid -D"')
		finally:
			p = subprocess.Popen(args)
