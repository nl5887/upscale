import boto.ec2

from upscale import config
config=config.config

access=config['ec2']['access-key']
key= config['ec2']['secret-key']
region = config['ec2']['region']
vpcid = config['ec2']['vpc-id']

ec2_conn = boto.ec2.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=access)

import pprint
from collections import namedtuple

def list():
	Host = namedtuple('Host', ['id', 'name', 'private_ip', 'ip'])

	# public_dns_name
	hosts = []
	for reservation in ec2_conn.get_all_instances(filters={'vpc-id': vpcid}):
		for instance in reservation.instances:
			hosts.append(Host(id= instance.id, name = instance.private_dns_name, private_ip = instance.private_ip_address, ip=instance.ip_address))
	
	return hosts


