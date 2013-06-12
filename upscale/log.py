import logging

# methods
getLogger = logging.getLogger
debug = logging.debug
info = logging.info
warning = logging.warning
warn = logging.warn
error = logging.error
exception = logging.exception
critical = logging.critical
log = logging.log

class UpscaleLogger(logging.Logger):
	def __init__(self, name, level=logging.NOTSET):
		logging.Logger.__init__(self, name, level)

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		self.addHandler(ch)
		self.setLevel(logging.DEBUG)

	def addHandler(self, handler):
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		return logging.Logger.addHandler(self, handler)

logging.setLoggerClass(UpscaleLogger)
logging.basicConfig()

