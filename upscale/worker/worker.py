import os
import socket
import run
import datetime 
import pprint

import upscale
from upscale.config import config
from upscale.db.model import Session, Namespace, Domain, Project, Template
from upscale.utils import lxc

datadir = os.path.join(os.path.dirname(os.path.realpath(upscale.__file__)), 'data')

class Worker(object):
	""" Various convenience methods to make things cooler. """

	def start(self, namespace, project):
		container = run.run(namespace, project)
		return (container)

	def wait(self, name, state='RUNNING'):
		lxc.wait(name, state)
		return (True)

	def destroy(self, name):
		print lxc.destroy(name)	
		return (True)

	def shutdown(self, name):
		print lxc.shutdown(name)	
		return (True)

	def get_containers(self):
		return (lxc.get_containers())
	
