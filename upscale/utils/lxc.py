#!/usr/bin/python

import sys, getopt, os
import shlex, subprocess

#import gevent_subprocess as subprocess

def start(name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-start', '-d', '-n', name],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def attach(name, command):	
	import subprocess
	#lxcls = subprocess.Popen(['lxc-attach', '-n', name, ] + shlex.split(command),stdout = subprocess.PIPE,)
	lxcls = subprocess.Popen(['lxc-attach', '-n', name, ], stdin=subprocess.PIPE, stdout = subprocess.PIPE,)
	return (lxcls.communicate(command)[0])

def clone(base, name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-clone', '-n', name, '-o', base],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def wait(name, state='RUNNING'):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-wait', '-n', name, '-s', state],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def destroy(name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-destroy', '-n', name],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def shutdown(name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-shutdown', '-n', name],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def stop(name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-stop', '-n', name],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def create(name):	
	import subprocess
	lxcls = subprocess.Popen(['lxc-create', '-t', 'ubuntu', '-n', name],stdout = subprocess.PIPE,)
	return (lxcls.communicate()[0])

def get_containers(type='running'):	
	import subprocess
	if (type=='all'):
		lxcls = subprocess.Popen(['lxc-ls',],stdout = subprocess.PIPE,)
	else:
		lxcls = subprocess.Popen(['lxc-ls','--running'],stdout = subprocess.PIPE,)
	return (filter(None, lxcls.communicate()[0].split('\n')))
		
