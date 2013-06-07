import sys, getopt, os
import argparse
import logging

from sqlalchemy.sql import exists
from upscale.db.model import (Session, Namespace, Project)

def create(namespace_arg):
	session=Session()

	if (session.query(exists().where(Namespace.name==namespace_arg)).scalar()):
		print "Namespace already exists"
		sys.exit(1)

	namespace = Namespace()
	namespace.name = namespace_arg 
	session.add(namespace)
	session.commit()

	# add key to authorized_keys

	import subprocess
	# use skeleton dir?
	s = subprocess.Popen(['useradd', '--base-dir', '/home', '-m', '-d', '/home/' + namespace.name, '--shell', '/usr/bin/git-shell', namespace.name, ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )
	logging.debug(s.communicate())
	
	import subprocess
	s = subprocess.Popen(['su', '-s', '/bin/sh', namespace.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, )

	from jinja2 import Template
	logging.debug(s.communicate(Template(
		"""
		mkdir /home/{{ namespace.name }}/git
		mkdir /home/{{ namespace.name }}/.ssh
		touch /home/{{ namespace.name }}/.ssh/authorized_keys

		# default upscale public key
                echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC81eMRpiQkq9IlIJK90NbGzuwgnAm529tDC2y6b4jZ0VgHkk/JQzUSZs9y6GntiSyTw/lsWQCAFVDztD+aN9ZF3f/wtYAYF2x3WZmudNTtdTlf9OyzWC5I9sUOsKRrk+xzk86lBuoEHzIMDP3y0+gGU1PlbksrC3oWTjnvOLs62aR2xjsrVieZ+TxK6ohm1hSiODdlCJu9ldG9IK1A6H6i5uPJgZDhUulKu5P9z1yNfrEB/EJU26y16U+z1RoGauJSgEbKeyoR2KeMcTUOZBUFWFr9vdjYMcnpXx973KoIS8n9MIYtwiaw0PtkDxc4Zbj03UFYS1Y7Dn6H0C5eIz07 root@ip-10-0-0-55 >> /home/{{ namespace.name }}/.ssh/authorized_keys

		""").render(namespace=namespace, )))

	os.mkdir(os.path.join('/data/', namespace.name))

	print "Namespace has been created."	
	
