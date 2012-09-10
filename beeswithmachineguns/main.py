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
from optparse import OptionParser, OptionGroup

NO_TRAILING_SLASH_REGEX = re.compile(r'^.*?\.\w+$')

def parse_options():
    
    """
    Handle the command line arguments for spinning up bees
    """     
    version = str(sys.version_info[0]) + "." + str(sys.version_info[1])
    float(version)
    s_kwargs = {'metavar' : "SERVERS",'nargs' : 1,'action' : 'store','dest' : 'servers','default':5}
    k_kwargs = {'metavar' : "KEY",'nargs' : 1,'action' : 'store','dest' : 'key'}
    g_kwargs = {'metavar' : "GROUP",'nargs' : '*','action' : 'store','dest' : 'group','default' : 'default'}    
    gg_kwargs = {'metavar' : "GROUP",'nargs' : 1,'action' : 'store','dest' : 'group','default' : 'default'}    
    z_kwargs = {'metavar' : "ZONE",'nargs' : 1,'action' : 'store','dest' : 'zone','default' : 'us-east-1d'}
    i_kwargs = {'metavar' : "INSTANCE",'nargs' : 1,'action' : 'store','dest' : 'instance','default' : 'ami-ff17fb96'}
    l_kwargs = {'metavar' : "LOGIN",'nargs' : 1,'action' : 'store','dest' : 'login','default' : 'newsapps'} 
    u_kwargs = {'metavar' : "URL",'nargs' : 1,'action' : 'store','dest' : 'url'} 
    n_kwargs = {'metavar' : "NUMBER",'nargs' : 1,'action' : 'store','dest' : 'number','default' : 1000}
    c_kwargs = {'metavar' : "CONCURRENT",'nargs' : 1,'action' : 'store','dest' : 'concurrent','default' : 100} 
    
    if float(version) >= 2.7:
	import argparse
        parser = argparse.ArgumentParser(add_help=True)
        
        subparsers = parser.add_subparsers(help='commands', dest='command')
        up_parser = subparsers.add_parser('up')
        attack_parser = subparsers.add_parser('attack')
        down_parser = subparsers.add_parser('down')
        report_parser = subparsers.add_parser('report')    
        
        # Required
        up_parser.add_argument('-k', '--key', **k_kwargs)
        up_parser.add_argument('-s','--servers', **s_kwargs)
        up_parser.add_argument('-g', '--group', **g_kwargs)
        up_parser.add_argument('-z', '--zone',**z_kwargs)
        up_parser.add_argument('-i', '--instance', **i_kwargs)
        up_parser.add_argument('-l', '--login', **l_kwargs)
        
        #attack_group = parser.add_argument_group('attack')
        # Required
        attack_parser.add_argument('-u', '--url', **u_kwargs)
        attack_parser.add_argument('-n', '--number', **n_kwargs)
        attack_parser.add_argument('-c', '--concurrent', **c_kwargs)
    
        options = parser.parse_args()

    else:
        #if version less than 2.7      
	parser = OptionParser(usage="""
            bees COMMAND [options]
            Bees with Machine Guns
            A utility for arming (creating) many bees (small EC2 instances) to attack
            (load test) targets (web applications).

            commands:
              up      Start a batch of load testing servers.
              attack  Begin the attack on a specific url.
              down    Shutdown and deactivate the load testing servers.
              report  Report the status of the load testing servers.
            """)

        up_group = OptionGroup(parser, "up", 
        """In order to spin up new servers you will need to specify at least the -k command, which is the name of the EC2 keypair to use for creating and connecting to the new servers. The bees will expect to find a .pem file with this name in ~/.ssh/.""")
        
	# Required
        up_group.add_option('-k', '--key', **k_kwargs)
        up_group.add_option('-s', '--servers', **s_kwargs)
        up_group.add_option('-g', '--group', **gg_kwargs)
        up_group.add_option('-z', '--zone',  **z_kwargs)
        up_group.add_option('-i', '--instance', **i_kwargs)
        up_group.add_option('-l', '--login',  **l_kwargs)

        parser.add_option_group(up_group)

        attack_group = OptionGroup(parser, "attack", 
            """Beginning an attack requires only that you specify the -u option with the URL you wish to target.""")

        # Required
        attack_group.add_option('-u', '--url', **u_kwargs)

        attack_group.add_option('-n', '--number', **n_kwargs)
        attack_group.add_option('-c', '--concurrent', **c_kwargs)

        parser.add_option_group(attack_group)

        (options, args) = parser.parse_args()
    
    
    if float(version) >=2.7:
	command = options.command
        if command == "up":
            options.key = options.key[0]
            options.zone = options.zone[0]
            options.servers = options.servers[0]
        elif command == "attack":
            options.url = options.url[0]
            options.number = options.number[0]
            options.concurrent = options.concurrent[0]
            
    else: 
        command = args[0]
          
        #command = args[0]
    if command == 'up':
        if not options.key:
            parser.error('To spin up new instances you need to specify a key-pair name with -k')
    
        if options.group == 'default':
            print 'New bees will use the "default" EC2 security group. Please note that port 22 (SSH) is not normally open on this group. You will need to use to the EC2 tools to open it before you will be able to attack.'
        bees.up(options.servers, options.group, options.zone, options.instance, options.login, options.key)
    elif command == 'attack':    
        if not options.url:
            parser.error('To run an attack you need to specify a url with -u')
    
        if NO_TRAILING_SLASH_REGEX.match(options.url):
            parser.error('It appears your URL lacks a trailing slash, this will disorient the bees. Please try again with a trailing slash.')
        
        bees.attack(options.url,options.number,options.concurrent)
    elif command  == 'down':
        bees.down()
    elif command == 'report':
        bees.report()
          
    
def main():
    parse_options()
