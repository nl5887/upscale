import sys, getopt, os
import argparse
import shlex
import yaml
import git
import shutil
import subprocess
import logging

from jinja2 import Template
import tempfile
import git

import upscale
datadir = os.path.join(os.path.dirname(os.path.realpath(upscale.__file__)), 'data')

from upscale import config
config = config.config

#from upscale.worker import tasks
import datetime

from upscale.db.model import (Session, Namespace, Project, Key, Repository)

# http://stackoverflow.com/questions/12641514/switch-to-different-user-using-fabric

def cmd(command):	
	lxcls = subprocess.Popen(shlex.split(command),stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def create(namespace_arg, application_arg, runtime_arg, repository_arg):
	if not os.path.exists(os.path.join(datadir, 'runtime/{0}.yaml').format(runtime_arg)):
		raise Exception ('Runtime {0} does not exist.'.format(runtime_arg))

	try:
		session = Session()
		namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

		project = Project()
		project.name = application_arg 
		project.template = runtime_arg 
		namespace.projects.append(project)
		 
		bi = yaml.load(file(os.path.join(datadir, 'runtime/{0}.yaml').format(project.template), 'r'))

		root = os.path.join(config['data'], namespace.name, )

		if not os.path.exists(os.path.join(root, project.name)):
			os.mkdir(os.path.join(root, project.name))

		# home = os.path.join(config['data'], namespace.name, 'home')

		from Crypto.PublicKey import RSA
		import base64
		key = RSA.generate(2048, os.urandom)

		project.key = Key()
		#project.key.private_key = key.exportKey('OpenSSH')
		project.key.private_key = key.exportKey()
		project.key.public_key = key.exportKey('OpenSSH')
		project.key.active = True

		project.repository = Repository()
		project.repository.url = repository_arg 
 
		# add registered (namespace) ssh keys!
		# also for generic user

		# using ssh because of ownership 
		"""
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
		"""

		session.commit()

		print "Application has been created. You can clone the git repository with \n" \
			"git clone {0} .".format(config['git']['public'].format(namespace.name, project.name))	

	except:
		session.rollback()
		logging.exception("Exception while creating application")

def start():
	pass

def run(namespace, project, ):
	import zmq
	context = zmq.Context()
	socket = context.socket(zmq.PUSH)
	socket.connect('tcp://127.0.0.1:5867')
	socket.send_pyobj((start, [namespace, project], {}))
	#socket.send_pyobj((start, ['remco1013', 'website3'], {}))

	print 'Starting application.'
	# start chained rebalance afterwards


