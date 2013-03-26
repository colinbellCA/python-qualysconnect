#!/usr/bin/env python
""" qscanhist
A script that takes a hostname or ip address and queries QualysGuard for
scan history.
"""
import sys
import logging
import datetime

from optparse import OptionParser

from qualysconnect.util import build_v1_connector
from qualysconnect.util import is_valid_ip_address, hostname_to_ip

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011-2013, University of Waterloo"
__license__ = "BSD-new"

def process_cli_arguments():
    """ Process arguments from sysv and return an option list representing the
    flags set on the command line.
    
    """
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Display detailed logging messages.", default=False)
    parser.add_option("-a", "--address", dest="hostip",
                      help="Display QualysGuard results for IP.", metavar="IP")
    parser.add_option("-H", "--hostname", dest="hostname",
                      help="Display QualysGuard results for HOSTNAME.",
                      metavar="HOSTNAME")
    
    (options, args) = parser.parse_args()
    
    # we did not get any values that might represent a host or ip. 
    if len(args) == 0 and not (options.hostip or options.hostname):
        parser.print_help()
        parser.error("an ip or hostname must be provided.")
    
    # either an address OR a hostname are provided.  NOT both.
    if options.hostip and options.hostname:
        parser.error("-a and -H options are mutually exclusive.")
    
    # maybe the user can't read and they didn't use a flag but provided a
    # reasonable value that we can attempt to convert to an IP or HOSTNAME?
    if not (options.hostip or options.hostname):
        if is_valid_ip_address(args[0]):
            options.hostip = args.pop()
        else:
            options.hostname = args.pop()

    # verify that there are no unprocessed arguments.
    if args:
            parser.error("unprocessed arguments-> [%s]"%(str(args),))
  
    return options

# BEGIN
#  main() function.  This is where the real 'meat' is.
if __name__ == '__main__':
    
    # process command line arguments and prepare info to submit for QualysGuard
    options = process_cli_arguments();
    
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)
    
    host = None
    
    if options.hostip:
        host = options.hostip
    elif options.hostname:
        host = hostname_to_ip(options.hostname)
    else:
        raise Exception('Critical Error. No IP computed to query.')
    
    # begin session with QualysGuard and process return.
    qgs=build_v1_connector()

    # calculate date 1 year (minus a day) in the past for query
    today = datetime.date.today()
    querydelta = datetime.timedelta(days=365-1)
    target = today - querydelta

    # request VM detection records from QualysGuard using APIv1
    ret = qgs.request("scan_target_history.php?date_from=%s&ip_targeted_list=1&ips=%s&"
            %(target.isoformat(),host,))
    
    print ret
