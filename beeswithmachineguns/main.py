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
PYTHON_VERSION = "%s.%s" % (sys.version_info[0], sys.version_info[1]) 

def parse_options():
    
    """
    Handle the command line arguments for spinning up bees
    """     
    config_options_up = (
             (('-k','--key'),      {'metavar' : "KEY",
                                    'nargs' : 1,
                                    'action' : 'store',
                                    'dest' : 'key',
                                    'help' : 'The ssh key pair name to use to connect to the new servers.'}),
             (('-s','--servers'),  {'metavar' : "SERVERS",
                                    'nargs' : 1,
                                    'action' : 'store',
                                    'dest' : 'servers',
                                    'default':5,
                                    'help' :'The number of servers to start (default: 5).'}),
             (('-g', '--group'),   {'metavar' : "GROUP",
                                    'nargs' : '*' if PYTHON_VERSION >= '2.7' else 1,
                                    'action' : 'store',
                                    'dest' : 'group',
                                    'default' : 'default',
                                    'help' : 'The security group to run the instances under (default: default).'}),
             (('-z', '--zone'),    {'metavar' : "ZONE",
                                    'nargs' : 1,
                                    'action' : 'store',
                                    'dest' : 'zone',
                                    'default' : 'us-east-1d',
                                    'help' : 'The availability zone to start the instances in (default: us-east-1d).'}),
             (('-i', '--instance'),{'metavar' : "INSTANCE",
                                    'nargs' : 1,
                                    'action' : 'store',
                                    'dest' : 'instance',
                                    'default' : 'ami-ff17fb96',
                                    'help' :'The instance-id to use for each server from (default: ami-ff17fb96).'}),
             (('-l', '--login'),   {'metavar' : "LOGIN",
                                    'nargs' : 1,
                                    'action' : 'store',
                                    'dest' : 'login',
                                    'default' : 'newsapps',
                                    'help' : 'The ssh username name to use to connect to the new servers (default: newsapps).'}))
    
    config_options_attack = [
            (('-u', '--url'),        {'metavar' : "URL",
                                      'nargs' : 1,
                                      'action' : 'store',
                                      'dest' : 'url',
                                      'help' : 'URL of the target to attack.'}),
             (('-n', '--number'),    {'metavar' : "NUMBER",
                                      'nargs' : 1,
                                      'action' : 'store',
                                      'dest' : 'number',
                                      'default' : 1000,
                                      'help' : 'The number of total connections to make to the target (default: 1000).'}),
             (('-c', '--concurrent'),{'metavar' : "CONCURRENT",
                                      'nargs' : 1,
                                      'action' : 'store',
                                      'dest' : 'concurrent',
                                      'default' : 100,
                                      'help' : 'The number of concurrent connections to make to the target (default: 100).'})]
    
    if PYTHON_VERSION >= "2.7":
        import argparse       
        parser = argparse.ArgumentParser(add_help=True)
        
        subparsers = parser.add_subparsers(help='commands', dest='command')
        up_parser = subparsers.add_parser('up')
        attack_parser = subparsers.add_parser('attack')
        down_parser = subparsers.add_parser('down')
        report_parser = subparsers.add_parser('report')    

        [up_parser.add_argument(*config_up[0],**config_up[1]) for config_up in config_options_up]
        
        [attack_parser.add_argument(*config_attack[0],**config_attack[1]) for config_attack in config_options_attack]   
        
        command, options = parse_opt(parser.parse_args())
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
        
        #up_parser.add_argument([(*config_up[0],**config_up[1]) for config_up in config_options_up])
        
        [parser.add_option(*config_up[0],**config_up[1]) for config_up in config_options_up]

        parser.add_option_group(up_group)

        attack_group = OptionGroup(parser, "attack", 
            """Beginning an attack requires only that you specify the -u option with the URL you wish to target.""")

        [parser.add_option(*config_attack[0],**config_attack[1]) for config_attack in config_options_attack]
        
        parser.add_option_group(attack_group)

        command, options = parse_opt(parser.parse_args())
        
    
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
          

def parse_opt(params):
    if PYTHON_VERSION >= "2.7":
        options = params
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
        options = params[0]
        command = params[1][0]
        if command == "up":
            options.group = get_groups(options.group)
        
    
    return command, options
            
                
def get_groups (group_str):
    return [group.strip() for group in group_str.split(',')]

def main():
    parse_options()
    