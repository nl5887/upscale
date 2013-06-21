from fabric.api import run, execute, task, settings, sudo, cd, prefix, env
from fabric.operations import put
from fabric.contrib import files

import sys, getopt, os
import argparse

def deploy():
	with settings():
		sudo('apt-get update -qq')

		# mysql or mariadb?
		sudo('apt-get install --force-yes -y -qq lxc haproxy python-jinja2 git xfsprogs btrfs-tools python-virtualenv mysql-server varnish')
	
		# install glusterfs
		sudo('apt-get install --force-yes -y -qq software-properties-common')
		sudo('add-apt-repository -y ppa:semiosis/ubuntu-glusterfs-3.3')
		sudo('apt-get update -qq')
		sudo('apt-get install --force-yes -y -qq glusterfs-server glusterfs-client')
		
		from socket import gethostname; 
		# assume server running bootstrap is server
		sudo('gluster peer probe %s' % gethostname())
		files.append ('/etc/fstab', '%s:/data /data nfs defaults,_netdev,mountproto=tcp,noac 0 0' % gethostname(), use_sudo=True)
		
		sudo('mkdir /data')
		sudo('mount /data')

		sudo('mkdir /opt/upscale')
		with cd('/opt/upscale'):
			sudo('git clone git://github.com/nl5887/upscale.git .')

		#change lxc instances folder
		sudo('mkdir /mnt/lxc')
		sudo('mv /var/lib/lxc /var/lib/lxc.bak')
		sudo('ln -s /mnt/lxc /var/lib/lxc')

		#files.upload_template("", "/etc/resolv.conf", use_sudo=True)
		try:
			with cd('/opt/upscale/'):
				sudo('virtualenv --system-site-packages env')
		except:
			pass

		with cd('/opt/upscale/'):
			sudo('apt-get install --force-yes -y -qq libmysqlclient-dev python-dev')
			with prefix('. ./env/bin/activate'):
				sudo('pip install jinja2 sqlalchemy mysql-python celery python-dateutil pytz gitpython')	


		# install database
		# sudo('curl http:///.sql | mysql -p upscale')
	
		with settings(warn_only=True):
			sudo ('killall haproxy')

		# reload not necessary

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--host', required=False, )
	parser.add_argument('--username', required=False, default='ubuntu', )
	parser.add_argument('-i', required=False, help='identity file')
	args = parser.parse_args()

	#env.use_ssh_config = True
	env.user = args.username
	
	if args.i:
		env.key_filename = args.i 
	
	print "Bootstrap will install Upscale. This is only tested on Ubuntu 13.04. "
	print "Installation will be executed remote using ssh."
	print "Press ENTER to continue or press Ctrl-C to abort the install process:"

	raw_input ("press enter to continue> ")

	if (args.host):
		execute(deploy, hosts=args.host.split(','))
	else:
		# local
		execute(deploy, hosts=['127.0.0.1'])
	
	print "Installation finished. Now you should configure upscale/conf/config.yaml and "
	print "start master and worker nodes."
	
if __name__ == "__main__":
	main()

