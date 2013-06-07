import sys, getopt, os
import argparse
import shlex
import yaml
import git
import shutil
import subprocess
from jinja2 import Template
import tempfile
import git

from upscale import config
config = config.config

from upscale.worker import tasks
import datetime

from upscale.db.model import (Session, Namespace, Project)

# http://stackoverflow.com/questions/12641514/switch-to-different-user-using-fabric

def cmd(command):	
	lxcls = subprocess.Popen(shlex.split(command),stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def create(namespace_arg, application_arg, runtime_arg):
	if not os.path.exists('/data/upscale/runtime/{0}.yaml'.format(runtime_arg)):
		print 'Runtime {0} does not exist.'.format(runtime_arg)
		return


	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

	project = Project()
	project.name = application_arg 
	project.template = runtime_arg 
	namespace.projects.append(project)
	session.commit()
	 
	bi = yaml.load(file('/data/upscale/runtime/{0}.yaml'.format(project.template), 'r'))

	s = subprocess.Popen(['su', '-s', '/bin/sh', namespace.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )

	# initialize bare git repository
	print s.communicate(Template(
		"""
		cd /home/{{ namespace.name }}/
		mkdir "/home/{{ namespace.name }}/git/{{ application.name }}.git"
		cd "/home/{{ namespace.name }}/git/{{ application.name }}.git"
		git init --template="/data/upscale/etc/git/" --bare "/home/{{ namespace.name }}/git/{{ application.name }}.git"
		""").render(namespace=namespace, application=project, ))

	# add registered (namespace) ssh keys!
	# also for generic user

	# using ssh because of ownership 
	dirpath = tempfile.mkdtemp()

	cloned_repo = git.Repo.clone_from(config['git']['ssh'].format(namespace.name, project.name), dirpath)
	
	print 'Repo cloned from {0}.'.format(config['git']['ssh'].format(namespace.name, project.name))
	index = cloned_repo.index


	if 'project' in bi:
		for template in bi['project'].keys():
			print 'Adding to repo ' + template
			with open(os.path.join (dirpath, template), "w") as fh:
				fh.write (
						Template(bi['project'][template]).render( namespace=namespace, application=project)
					 )
			index.add([template])

	new_commit = index.commit("Upscale initial commit.")
	origin = cloned_repo.remotes.origin
	origin.push(cloned_repo.head)

	# clean up temp folder
        shutil.rmtree(dirpath)

	print "Application has been created. You can clone the git repository with \n" \
		"git clone {0} .".format(config['git']['public'].format(namespace.name, project.name))	

def run(namespace, project, host):

	# start container
        containers={}
        for i in tasks.get_instances():
                a=tasks.get_containers.apply_async(queue=i.id, routing_key=i.id, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), )
                containers[i.id] = a.get()

	min_host = host 
	if not host:
		for host in containers:
			if (not min_host or len(containers[host])<len(containers[min_host])):
				min_host=host
				pass

	print 'Starting container on host {0}.'.format(min_host)

	# prevent running same container on min_host
	container = tasks.start.apply_async(kwargs={'namespace':namespace, 'project':project}, queue=min_host, routing_key=min_host, expires=datetime.datetime.now()+datetime.timedelta(seconds=5), ).get()

	print 'Started container {1} on host {0}.'.format(min_host, container)
	# start chained rebalance afterwards


