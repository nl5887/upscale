from fabric.api import run, execute, task, settings, sudo, cd, prefix, env
from fabric.operations import put
from fabric.contrib import files

import sys, getopt, os
import argparse

def deploy():
	with settings():
		sudo('apt-get update -qq')
		sudo('apt-get install --force-yes -y -qq lxc haproxy python-jinja2 git xfsprogs btrfs-tools python-virtualenv varnish')
		
		# convert filesystem to btrfs
		sudo('umount /mnt/')
		sudo('mkfs.btrfs /dev/xvdb')
		sudo('mount /mnt')

		# install glusterfs
		sudo('apt-get install --force-yes -y -qq software-properties-common')
		sudo('add-apt-repository -y ppa:semiosis/ubuntu-glusterfs-3.3')
		sudo('apt-get update -qq')
		sudo('apt-get install --force-yes -y -qq glusterfs-server glusterfs-client')
		
		#sudo('gluster peer probe ip-10-0-0-55')
		files.append ('/etc/fstab', 'ip-10-0-0-47:/data /data nfs defaults,_netdev,mountproto=tcp,noac 0 0', use_sudo=True)
		sudo('mkdir /data')
		sudo('mount /data')

		#change lxc instances folder
		sudo('mkdir /mnt/lxc')
		sudo('mv /var/lib/lxc /var/lib/lxc.bak')
		sudo('ln -s /mnt/lxc /var/lib/lxc')

		files.put('templates/etc/init.d/celeryd', '/etc/init.d/celeryd', use_sudo=True, mode=0755)
		files.put('templates/etc/default/celeryd', '/etc/default/celeryd', use_sudo=True)

		#files.upload_template("", "/etc/resolv.conf", use_sudo=True)
		try:
			with cd('/root/'):
				sudo('virtualenv --system-site-packages env')
		except:
			pass

		with cd('/root/'):
			sudo('apt-get install --force-yes -y -qq libmysqlclient-dev python-dev')
			with prefix('. /root/env/bin/activate'):
				sudo('pip install jinja2 sqlalchemy mysql-python celery python-dateutil pytz gitpython')	

		with settings(warn_only=True):
			sudo ('killall haproxy')

		with settings(warn_only=True):
			with cd('/data/bin'):
				with prefix('. /root/env/bin/activate'):
					sudo ('/etc/init.d/celeryd create-paths')
					sudo ('/etc/init.d/celeryd restart')

		# reload not necessary

import boto.ec2

from upscale import config
config=config.config

access=config['ec2']['access-key']
key= config['ec2']['secret-key']

#ec2_conn = boto.ec2.connect_to_region('eu-west-1', aws_access_key_id=key, aws_secret_access_key=access)
#ec2_conn.run_instances(image_id='', instance_type='m1.small', 'security_group_ids')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--host', required=True, )
	parser.add_argument('--username', required=False, default='ubuntu', )
	parser.add_argument('-i', required=False, help='identity file')
	args = parser.parse_args()

	#env.use_ssh_config = True
	env.user = args.username
	
	if args.i:
		env.key_filename = args.i 
		
	execute(deploy, hosts=args.host.split(','))

if __name__ == "__main__":
	main()

