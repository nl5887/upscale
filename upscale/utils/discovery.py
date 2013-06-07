import boto.ec2
from config import config

access=config['ec2']['access-key']
key= config['ec2']['secret-key']

ec2_conn = boto.ec2.connect_to_region('eu-west-1', aws_access_key_id=key, aws_secret_access_key=access)

print ec2_conn

ec2_conn.region='eu-west-1'
print ec2_conn
import pprint


for reservation in ec2_conn.get_all_instances(filters={'vpc-id':'vpc-52eaf63a'}):
	for instance in reservation.instances:
		pprint.pprint( instance.private_dns_name)
		pprint.pprint( instance.private_ip_address)

#print ec2_conn.get_all_instances()

