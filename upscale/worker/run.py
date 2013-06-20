#!/usr/bin/python

import sys, getopt, os
import shlex, subprocess
import yaml

from datetime import datetime
from jinja2 import Environment, PackageLoader, Template

from fabric.api import run, execute, task, settings, sudo, cd, prefix, env
from fabric.operations import put
from fabric.contrib import files

import upscale

from upscale.db.model import (Session, Project, Namespace)
from upscale.utils import lxc
from upscale import config

config=config.config


def chroot(path, command):        
        import subprocess 
        lxcls = subprocess.Popen(['chroot', path], stdin = subprocess.PIPE, stdout = subprocess.PIPE,) 
        return (lxcls.communicate(command)[0]) 

def cmd(command):	
	import subprocess
	lxcls = subprocess.Popen(shlex.split(command),stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])
		
def run (namespace, project):
	datadir = os.path.join(os.path.dirname(os.path.realpath(upscale.__file__)), 'data')
	print datadir

	session = Session()
	namespace = session.query(Namespace).filter(Namespace.name==namespace).first()
	if (not namespace):
		raise Exception("Unknown namespace")

	project = namespace.projects.filter(Project.name==project).first()
	if (not project):
		raise Exception("Unknown project")

	from datetime import date
	bi = yaml.load(file(os.path.join(datadir, 'runtime/{0}.yaml').format(project.template), 'r'))	
	
	container="{0}_{1}_{2}".format(namespace.name, project.name, datetime.now().strftime("%y%m%d%H%M%S"))
	rootfs="/var/lib/lxc/{0}/rootfs".format(container)
	mirror="http://archive.ubuntu.com/ubuntu"
	security_mirror="http://security.ubuntu.com/ubuntu"
	release="raring"
	base=project.template + '_' + str(bi['version'])

	print ("Using runtime {0}".format(base))

	print (lxc.create(container,))
	
	datadir  = os.path.join (rootfs, "data")
	if not os.path.exists(datadir):
		os.mkdir(datadir)

	cmd("mount --bind /data/{0}/{1} {2}/data".format(namespace.name, project.name, rootfs))

	print lxc.start(container)
	print lxc.wait(container)

	print 'waiting 15 seconds'	
	import time
	time.sleep(15)

	import StringIO
	from fabric.api import run, execute, task, settings, sudo, cd, prefix, env
	with settings(user='ubuntu', password='ubuntu', host_string=container):
		sudo('apt-get update -qq')
	
		# install basic packages	
		sudo('apt-get install --force-yes -y -qq git', shell=False)

		# configure ssh
		sudo('mkdir -p /root/.ssh')

		with (cd('/root/.ssh')):
			# disable stricthostkeychecking
			put(StringIO.StringIO('Host *\n    StrictHostKeyChecking no'), 'config', use_sudo=True, mode=0600)
			put(StringIO.StringIO(project.key.public_key), 'id_rsa.pub', use_sudo=True, mode=0600)
			put(StringIO.StringIO(project.key.private_key), 'id_rsa', use_sudo=True, mode=0600)

		sudo('chmod 700 /root/.ssh')
		sudo('chmod 600 /root/.ssh/*')
		sudo('chown -R root:root /root/.ssh')

		# get template
		with (cd('/tmp/')):
			sudo('git clone git://github.com/nl5887/upscale-runtime-{0}.git upscale-runtime'.format(project.template))

		# fetch repository
		sudo('mkdir -p /repo/')

		with (cd('/repo/')):
			sudo('git init')
			sudo('git remote add origin {0}'.format(project.repository.url))
			sudo('git fetch origin')
			sudo('git checkout -b master')
			sudo('git reset origin/master --hard')
	
		# execute build scripts	
		with (cd('/tmp/upscale-runtime')):
			sudo('chmod +x ./build && ./build')
		
	# check for app.yaml
	ci={}

	#if (os.path.exists(os.path.join(rootfs, 'var/www/app.yaml'))):
	#	# load configuration
	#	ci = yaml.load(file(os.path.join(rootfs, 'var/www/app.yaml'), 'r'))
	#	pass		

	return (container)

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hp:n:",["project=","namespace="])
	except getopt.GetoptError:
		print 'runapp -n <namespace> -p <project>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'runapp -n <namespace> -p <project>'
			sys.exit()
		elif opt in ("-n", "--namespace"):
			namespace = arg
		elif opt in ("-p", "--project"):
			project = arg

	run (namespace, project)

if __name__ == "__main__":
   main(sys.argv[1:])

