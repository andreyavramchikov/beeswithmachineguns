#!/bin/env python

"""
The MIT License

Copyright (c) 2010 The Chicago Tribune & Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import bees
import re
import sys
import argparse

NO_TRAILING_SLASH_REGEX = re.compile(r'^.*?\.\w+$')

def parse_options():
    """
    Handle the command line arguments for spinning up bees
    """
    command = sys,
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(help='commands', dest='command')

    up_parser = subparsers.add_parser('up')
    attack_parser = subparsers.add_parser('attack')
    down_parser = subparsers.add_parser('down')
    report_parser = subparsers.add_parser('report')	

    # Required
    up_parser.add_argument('-k', '--key', metavar="KEY", nargs=1,
                        action='store', dest='key')
    up_parser.add_argument('-s', '--servers', metavar="SERVERS", nargs=1,
                        action='store', dest='servers', default=5)
    up_parser.add_argument('-g', '--group', metavar="GROUP", nargs="*",
                        action='store', dest='group', default='default')
    up_parser.add_argument('-z', '--zone', metavar="ZONE", nargs=1,
                        action='store', dest='zone', default='us-east-1d')
    up_parser.add_argument('-i', '--instance', metavar="INSTANCE", nargs=1,
                        action='store', dest='instance', default='ami-ff17fb96')
    up_parser.add_argument('-l', '--login', metavar="LOGIN", nargs=1,
                        action='store', dest='login', default='newsapps',
                        help="The ssh username name to use to connect to the new servers (default: newsapps).")


    #attack_group = parser.add_argument_group('attack')
    # Required
    attack_parser.add_argument('-u', '--url', metavar="URL", nargs=1,
                        action='store', dest='url', help="URL of the target to attack.")

    attack_parser.add_argument('-n', '--number', metavar="NUMBER", nargs=1,
                        action='store', dest='number', default=1000,
                        help="The number of total connections to make to the target (default: 1000).")
    attack_parser.add_argument('-c', '--concurrent', metavar="CONCURRENT", nargs=1,
                        action='store', dest='concurrent', default=100,
                        help="The number of concurrent connections to make to the target (default: 100).")
    attack_parser.add_argument('-l', '--login', metavar="LOGIN", nargs=1,
                        action='store', dest='login', default='attack')
    
    args = parser.parse_args()

    print args
	
    #command = args[0]
    if args.command == 'up':
        if not args.key:
            parser.error('To spin up new instances you need to specify a key-pair name with -k')

        if args.group == 'default':
            print 'New bees will use the "default" EC2 security group. Please note that port 22 (SSH) is not normally open on this group. You will need to use to the EC2 tools to open it before you will be able to attack.'
	print args
        bees.up(args.servers[0],args.group,args.zone[0], args.instance, args.login, args.key[0])
    elif args.command == 'attack':	
	url = args.url[0]   
	if not url:
            parser.error('To run an attack you need to specify a url with -u')

        if NO_TRAILING_SLASH_REGEX.match(url):
            parser.error('It appears your URL lacks a trailing slash, this will disorient the bees. Please try again with a trailing slash.')
	number = args.number
		
	concurrent = args.concurrent      
	bees.attack(url,int(number[0]),int(concurrent[0]))
    elif args.command  == 'down':
        bees.down()
    elif args.command == 'report':
        bees.report()


def main():
    parse_options()

