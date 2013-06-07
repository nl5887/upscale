import yaml
import os

config= None
for loc in [os.path.dirname(os.path.realpath(__file__)), os.path.join(os.path.dirname(os.path.realpath(__file__)), 'conf'), "/etc/upscale", ]:
	try: 
		with open(os.path.join(loc, "config.yaml"), 'r') as c:
			config = yaml.load(c)
	except IOError:
		pass

if config is None:
	raise Exception("Configuration file not found.")
