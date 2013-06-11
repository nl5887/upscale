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

	if (not base in lxc.get_containers('all')):
			baserootfs="/var/lib/lxc/{0}/rootfs".format(base)
			
			# create template container
			print (lxc.create(base))
			
			#bi = yaml.load(file('{0}.yaml'.format(project.template), 'r'))
			# always update
			print (chroot (baserootfs, r"apt-get update"))

			# chroot or lxc-attach? 
			# install packages
			if bi['packages']:
				print (chroot (baserootfs, r"apt-get install --force-yes -y " + ' '.join(bi['packages'])))

			#stop (base)		

	# mount http://stackoverflow.com/questions/6469557/mounting-fuse-gives-invalid-argument-error-in-python

	# clone of runtime for speed
	print (lxc.clone(base, container))
	
	datadir  = os.path.join (rootfs, "data")
	if not os.path.exists(datadir):
		os.mkdir(datadir)

	cmd("mount --bind /data/{0}/{1} {2}/data".format(namespace.name, project.name, rootfs))

	print lxc.start(container)
	
	# should we use cloud init for configuration instead of lxc-attach?
	# The -u option accepts a cloud-init user-data file to configure the container on start. If -L is passed, then no locales will be installed.
	print lxc.wait(container)

	#env.user = args.username
	#env.key_filename = args.i 
	#env.password=
	#execute(deploy, hosts=args.host.split(','))

	# or should we use fabric for this?
	print lxc.attach(container, "rm -df /var/www/*")

	#if os.path.isdir(DIR_NAME):
	#	shutil.rmtree(DIR_NAME)

	#os.mkdir(DIR_NAME)

	# should we do this inside container?
	from git import Repo
	Repo.clone_from(config['git']['url'].format(namespace.name, project.name), os.path.join(rootfs, 'var/www/'))

	# check for app.yaml
	ci={}

	if (os.path.exists(os.path.join(rootfs, 'var/www/app.yaml'))):
		# load configuration
		ci = yaml.load(file(os.path.join(rootfs, 'var/www/app.yaml'), 'r'))
		pass		
	
	# should we do this inside container?
	import shutil

	files={}

	if (bi.get('files')):
		files.update(bi['files'])

	if (ci.get('files')):
		files.update(ci['files'])

	for template in files.keys():
		print 'Creating file ' + template[1:]
		with open(os.path.join (rootfs, template[1:]), "w") as fh:
			params = {}
			for p in project.parameters:
				params[p.key]=p.value

			for p in bi.keys():
				params[p]=bi[p]

			for p in ci.keys():
				params[p]=ci[p]

			fh.write (
					Template(files[template]).render(params)
				 )


	if (bi.get('install')):
		print lxc.attach(container, bi['install'] )

	if (ci.get('install')):
		print lxc.attach(container, ci['install'] )

	return (container)
	#from tasks import reload
	#reload.delay()

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

