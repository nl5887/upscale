# -*- coding: utf-8 -*-

# based on 
# http://www.gefira.pl/blog/2011/07/01/accessing-haproxy-statistics-with-python/ 
from __future__ import absolute_import, division, print_function, unicode_literals
 
# stdlib
import logging
import socket
import select
import sys
import socket
import string

from time import time
from traceback import format_exc
 
logger = logging.getLogger(__name__)
 
class HAProxyStats(object):
	""" Used for communicating with HAProxy through its local UNIX socket interface.
	"""
	def __init__(self, socket_name=None):
		self.socket_name = socket_name
 
	def execute(self, command, extra="", timeout=200):
		""" Executes a HAProxy command by sending a message to a HAProxy's local
		UNIX socket and waiting up to 'timeout' milliseconds for the response.
		"""
 
		if extra:
			command = command + ' ' + extra
 
		buffer = ""
 
		client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client.connect(self.socket_name)

		client.send(command + "\n")

		while(True):
			r, w, e = select.select([client,],[],[])
			for x in r:
				if (x==client):
					buffer = buffer + client.recv(4096).decode('utf-8')
					if (len(buffer)==0):
						raise Exception("closed")	
										
					lines=buffer.split('\n')
					buffer = lines.pop()
					for line in lines:
						print (line)


def main():
	#from haproxy import HAProxyStats
	#stats = HAProxyStats('/tmp/haproxy.sock')
	#stats.execute("show info")

