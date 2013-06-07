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
import base64
import logging

from sqlalchemy.sql import exists
from sqlalchemy.sql import and_, or_, not_

from upscale import config
config = config.config

from upscale.db.model import (Session, Namespace, Project, Key)


def add(namespace_arg, name_arg, public_arg):
	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

	from sqlalchemy.sql import exists
	from sqlalchemy.sql import and_, or_, not_

        if (namespace.keys.filter(and_(Key.name==name_arg, Key.active==True)).first()):
                raise Exception('Key already exists')

        if (namespace.keys.filter(and_(Key.public==public_arg, Key.active==True)).first()):
                raise Exception('Key already exists')

	# validate public key
	values = public_arg.split()

	if (len(values)==2):
		data = base64.decodestring(values[1])
		if (data[4:11] != values[0]):
			raise Exception("Invalid ssh key")
	elif (len(values)==3):
		data = base64.decodestring(values[1])
		if (data[4:11] != values[0]):
			raise Exception("Invalid ssh key")
	else:
		raise Exception("Invalid ssh key")

	key = Key()
	key.name = name_arg 
	key.public = public_arg 
	key.active = True
	namespace.keys.append(key)
	session.commit()
	
	# update git repository for namespace
	update(namespace)

def delete(namespace_arg, name_arg, ):
	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

        key = namespace.keys.filter(and_(Key.name==name_arg, Key.active==True)).first()

	if not key:
                raise Exception('Key not found.')

	key.active=False
	session.commit()

	update(namespace)

def list(namespace_arg):
	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()
	return (namespace.keys.filter(Key.active==True))

# should be actually using a celery task on right (git) host
def update(namespace):
        import subprocess

	from jinja2 import Template
	s = subprocess.Popen(['su', '-s', '/bin/sh', namespace.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )
	logging.debug(s.communicate(Template(
		"""
		# remove existing keys
		echo "{{ config['public-key'] }} " > /home/{{ namespace.name }}/.ssh/authorized_keys
		
		# recreate
		{% for key in keys %}
		echo "{{ key.public }}" >> /home/{{ namespace.name }}/.ssh/authorized_keys
		{% endfor %}
		""").render(namespace=namespace, keys=namespace.keys.filter(Key.active==True), config=config )))


