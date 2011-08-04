#!/usr/bin/env python
""" qreports
A script that initiates a QualysGuard report, checks if a report has finished
generating, and allows download of the report results.

"""
import sys
import logging
import datetime

from optparse import OptionParser

from qualysconnect.util import build_v2_session
from qualysconnect.util import is_valid_ip_address, hostname_to_ip

from qualysconnect.qg.xmlproc import QGXP_lxml_objectify, QGXP_qgdt_to_datetime

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011, University of Waterloo"
__license__ = "BSD-new"

def process_cli_arguments():
    """ Process arguments from sysv and return an option list representing the
    flags set on the command line.
    
    """
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Display detailed logging messages.", default=False)
    parser.add_option("-s", "--list-scans", action="store_true", dest="listscans",
                      help="List scan results known to Qualys.", default=False)
    parser.add_option("-t", "--scan-type", dest="scantype",
                      help="Specify the type of scans to list", default=None)
    
    (options, args) = parser.parse_args()
    
    # verify we got something.
    if not options.listscans:
        parser.print_help()
        parser.error("Need arguments.")
    
    # scantype can only be set if listscans was requested.
    if options.scantype and not options.listscans:
        parser.print_help()
        parser.error("scan type (-t) can only be specified with (-s) option.")
    
    # verify that there are no unprocessed arguments.
    if args:
            parser.error("unprocessed arguments-> [%s]"%(str(args),))
  
    return options

def display_QG_scanlist(scanlist):
#    from lxml import objectify
    for scan in scanlist.RESPONSE.SCAN_LIST.SCAN:
#        print objectify.dump(scan)
        print "REFERENCE:\t%s"%(scan.REF,)
        print "TITLE:\t\t%s"%(scan.TITLE,)
        print "LAUNCH DT:\t%s"%(QGXP_qgdt_to_datetime(scan.LAUNCH_DATETIME,))
        print "TARGET:\t\t%s"%(scan.TARGET,)
        print "\n"

# BEGIN
#  main() function.  This is where the real 'meat' is.
if __name__ == '__main__':
    
    # process command line arguments and prepare info to submit for QualysGuard
    options = process_cli_arguments();
    
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)
    
    # begin session with QualysGuard and process return.
    qgs=build_v2_session()
    qgs.connect()

    # if requested, fetch and display scan result sets known to QualysGuard
    if options.listscans:
        if options.scantype:
            ret = qgs.request("scan/?action=list&state=Finished&type=%s"
                              %(options.scantype,))
        else:
            ret = qgs.request("scan/?action=list&state=Finished")
        
        display_QG_scanlist(QGXP_lxml_objectify(ret))
    
 #   print ret

    qgs.disconnect()