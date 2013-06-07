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

from upscale.db.model import (Session, Namespace, Project, Domain)

def add(namespace_arg, application_arg, domain_arg):
	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

	if not namespace:
		raise Exception ('Namespace not found')

	# should check domain text field if user owns this domain

	application = namespace.projects.filter(Project.name==application_arg).first()
	if not application:
		raise Exception ('Application not found')

        if (application.domains.filter(and_(Domain.name ==domain_arg, Domain.active==True)).first()):
                raise Exception('Domain already exists')

	domain = Domain()
	domain.name = domain_arg 
	domain.active = True
	application.domains.append(domain)
	session.commit()

	# update haproxy celery task
	
def delete(namespace_arg, application_arg, domain_arg):
	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace_arg).one()

	if not namespace:
		raise Exception ('Namespace not found')

	application = namespace.projects.filter(Project.name==application_arg).first()
	if not application:
		raise Exception ('Application not found')

        domain = application.domains.filter(and_(Domain.name ==domain_arg, Domain.active==True)).first()

	if not domain:
                raise Exception('Domain doesn\'t exists')

	session = Session()
	domain.active=False
	session.commit()

	# update haproxy celery task
