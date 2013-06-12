import zmq

import gevent
import gevent.event

import time
import sys
import traceback

import logging

class Server(object):
	def __init__(self, url, objects):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.url = url 
		self.objects = objects

	def __enter__(self):
                self.socket.bind(self.url)
                return self

	def __exit__(self, type, value, traceback):
		self.socket.close()

	def run(self):
		while True:
			try:
				(cls, cmd, args, kwargs) = self.socket.recv_pyobj()
				print cls, cmd, args, kwargs

				if (cmd.startswith('_')):
					# private function
					raise Exception('Private functions not allowed.')

				c = self.objects[cls]

				try:
					f = getattr(c, cmd)
				except AttributeError:
					raise Exception('Unknown function')

				print f

				ret = f(*args, **kwargs)	
				print ret

				self.socket.send_pyobj(ret)
			except Exception, e:
				#exc_infos = list(sys.exc_info())
				#socket.send_pyobj(exc_infos)
				print e
				traceback.print_exc()
				self.socket.send_pyobj(e)


class RemoteClient(object):
	def __init__(self, url):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.url = url 
		pass

	def __enter__(self):
		self.socket.connect(self.url)
		return self

        def __exit__(self, type, value, traceback):
		self.socket.close()

	def _process(self):
		o = self.socket.recv_pyobj()
		if isinstance(o, Exception):
			raise o
		return (o)

	def __getattr__(self, method):
        	return lambda *args, **kargs: self(method, *args, **kargs)

	def __call__(self, method, *args, **kargs):
		self.socket.send_pyobj((self.__class__.__name__, method, args, kargs))

		# check for gevent
		import gevent
		try:
			async_result = gevent.event.AsyncResult()
			gevent.spawn(self._process).link(async_result)
			return async_result 
		except:
			o = self.socket.recv_pyobj()
			if isinstance(o, Exception):
				raise o
			return (o)

