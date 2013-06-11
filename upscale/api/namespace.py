import sys, getopt, os
import argparse
import logging

from sqlalchemy.sql import exists
from upscale.db.model import (Session, Namespace, Project)
from upscale import config
config = config.config

def create(namespace_arg):
	session=Session()

	if (session.query(exists().where(Namespace.name==namespace_arg)).scalar()):
		print "Namespace already exists"
		sys.exit(1)

	try:
		namespace = Namespace()
		namespace.name = namespace_arg 
		session.add(namespace)

		# add key to authorized_keys

		import subprocess
		# use skeleton dir?
		os.mkdir(os.path.join(config['data'], namespace.name))

		home = os.path.join(config['data'], namespace.name, 'home')

		s = subprocess.Popen(['useradd', '-m', '-d', home, '--shell', '/usr/bin/git-shell', namespace.name, ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )
		logging.debug(s.communicate())
		
		import subprocess
		s = subprocess.Popen(['su', '-s', '/bin/sh', namespace.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )

		from jinja2 import Template
		logging.debug(s.communicate(Template(
			"""
			mkdir {{home}}/git
			mkdir {{home}}/.ssh
			touch {{home}}/.ssh/authorized_keys
			""").render(home = home )))
		
		session.commit()

		print "Namespace has been created."	
	except:
		session.rollback()
		logging.exception("Exception while creating namespace.")
	
