#!/usr/bin/python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import sys, getopt, os
import argparse

POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))

if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'upscale', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from upscale import config

from upscale.api import application, containers, namespace, hosts, keys, domain

class Namespace(object):
	@staticmethod
	def create(args):
		namespace.create(args.namespace)

class Keys(object):
	@staticmethod
	def add(args):
		keys.add(args.namespace, args.name, args.public)

	@staticmethod
	def delete(args):
		keys.delete(args.namespace, args.name, )

	@staticmethod
	def list(args):
		for k in keys.list(args.namespace):
			print k.name

class Domain(object):
	@staticmethod
	def add(args):
		domain.add(args.namespace, args.application, args.domain)
		print 'Domain has been added'

	@staticmethod
	def delete(args):
		domain.delete(args.namespace, args.application, args.domain)
		print 'Domain has been deleted'

class Application(object):
	@staticmethod
	def create(args):
		application.create(args.namespace, args.application, args.runtime)
		print 'Key has been added'

	@staticmethod
	def run(args):
		application.run(args.namespace, args.application, args.host)

class Hosts(object):
	@staticmethod
	def list(args):
		for host in hosts.list():
			print '{0:<10}\t{1:<45}\t{2:<15}\t{3:<15}'.format(host.id, host.name, host.private_ip, host.ip)

class Container(object):
	@staticmethod
	def shutdown(args):
		containers.shutdown(args.host, args.container)	

	@staticmethod
	def status(args):
		for k, v in containers.status().iteritems():
			print '{0} ({1})'.format(k, ', '.join(v)) 

def main():
	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers(dest='module', help='sub-command help')

	parser_a = subparsers.add_parser('namespace', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')
	parser_aa = subparsers_a.add_parser('create', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.set_defaults(func=Namespace.create)

	parser_a = subparsers.add_parser('domain', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')

	parser_aa = subparsers_a.add_parser('add', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--application', required=True)
	parser_aa.add_argument('--domain', required=True)
	parser_aa.set_defaults(func=Domain.add)

	parser_aa = subparsers_a.add_parser('delete', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--application', required=True)
	parser_aa.add_argument('--domain', required=True)
	parser_aa.set_defaults(func=Domain.delete)

	parser_a = subparsers.add_parser('app', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')
	parser_aa = subparsers_a.add_parser('create', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--application', required=True)
	parser_aa.add_argument('--runtime', required=True)
	parser_aa.set_defaults(func=Application.create)

	parser_aa = subparsers_a.add_parser('run', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--application', required=True)
	parser_aa.add_argument('--host', required=True)
	parser_aa.set_defaults(func=Application.run)

	parser_a = subparsers.add_parser('containers', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')
	parser_aa = subparsers_a.add_parser('status', help='a help')
	parser_aa.set_defaults(func=Container.status)

	parser_aa = subparsers_a.add_parser('shutdown', help='a help')
	parser_aa.add_argument('--container', required=True)
	parser_aa.add_argument('--host', required=True)
	parser_aa.set_defaults(func=Container.shutdown)

	parser_a = subparsers.add_parser('hosts', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')
	parser_aa = subparsers_a.add_parser('list', help='a help')
	parser_aa.set_defaults(func=Hosts.list)

	parser_a = subparsers.add_parser('keys', help='a help')
	subparsers_a = parser_a.add_subparsers(dest='action', help='sub-command help')
	parser_aa = subparsers_a.add_parser('add', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--name', required=True)
	parser_aa.add_argument('--public', required=True)
	parser_aa.set_defaults(func=Keys.add)
	parser_aa = subparsers_a.add_parser('delete', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.add_argument('--name', required=True)
	parser_aa.set_defaults(func=Keys.delete)
	parser_aa = subparsers_a.add_parser('list', help='a help')
	parser_aa.add_argument('--namespace', required=True)
	parser_aa.set_defaults(func=Keys.list)

	args = parser.parse_args()

	if (args.func):
		args.func(args)

if __name__ == "__main__":
   main()

