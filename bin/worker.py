import os
import socket
import datetime 
import pprint
import sys

POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))

if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'upscale', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from upscale.utils.rpc import Server

import time
import sys
import traceback

from upscale.worker.worker import Worker

if __name__ == '__main__':
	from upscale.worker import tasks
	with Server("tcp://0.0.0.0:10000", {'Tasks': tasks, 'Worker': Worker()}) as s:
		s.run()

