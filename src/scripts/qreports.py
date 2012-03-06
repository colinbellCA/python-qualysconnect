#!/usr/bin/env python
""" qreports
A script that initiates a QualysGuard report, checks if a report has finished
generating, and allows download of the report results.

"""
import sys
import logging
import datetime

from optparse import OptionParser

from qualysconnect.util import build_v1_connector, build_v2_session
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
    parser.add_option("-S", "--list-scans", action="store_true", dest="listscans",
                      help="List scan results known to Qualys.", default=False)
    parser.add_option("-s", "--scan-type", dest="scantype",
                      help="Specify the type of scans to list", default=None)
    parser.add_option("-R", "--list-report", action="store_true", dest="listreports",
                      help="List known report templates.", default=False)
    
    # Options pertaining to launching a report.
    parser.add_option("-L", "--launch", action="store_true", dest="launchrpt",
                      help="Launch a report (provide -n, -r, -o)", default=False)
    parser.add_option("-n", dest="rpt_n",
                      help="The report template ID to launch.", default=None)
    parser.add_option("-r", dest="rpt_r",
                      help="The scan numbers you would like to use.", default=None)
    parser.add_option("-o", dest="rpt_o",
                      help="The output format you would like for your report.",
                      default=None)
    parser.add_option("-i", dest="rpt_i",
                      help="The IP set that you want to report on.",
                      default=None)
    parser.add_option("-t", dest="rpt_t",
                      help="The generated report title.", default=None)
    # Options pertaining to seeing the progress of a report.
    parser.add_option("-P", "--progress", dest="prog_n",
                      help="Show the progress of a given report.")
    # Options pertaining to downloading a report.
    parser.add_option("-D", "--download", dest="dl_n",
                      help="Download the results from a report.")
    
    (options, args) = parser.parse_args()
    
    if not ( options.listscans or options.listreports or options.launchrpt
               or options.prog_n or options.dl_n):
        parser.print_help()
        parser.error("Need arguments")
    
    if options.listscans and ( options.listreports or options.launchrpt ):
        parser.print_help()
        parser.error("")
    
    # scantype can only be set if listscans was requested.
    if options.scantype and not options.listscans:
        parser.print_help()
        parser.error("scan type (-t) can only be specified with (-s) option.")
        
    if options.launchrpt and not (options.rpt_n and options.rpt_r
                                  and options.rpt_o and options.rpt_t):
        parser.error("you must provide all RPT_* fields to launch a report.")
    
    # verify that there are no unprocessed arguments.
    if args:
            parser.error("unprocessed arguments-> [%s]"%(str(args),))
  
    return options

def display_QG_scanlist(scanlist):
    """ Displays a QualysGuard scanlist in an easy to copy/paste format.
    
    """
#    from lxml import objectify
    for scan in scanlist.RESPONSE.SCAN_LIST.SCAN:
#        print objectify.dump(scan)
        scandt = QGXP_qgdt_to_datetime(scan.LAUNCH_DATETIME)
        print "[%s]\t{( %s | %s )}"%(scan.REF, scandt, scan.TITLE)

def display_QG_report_template_list(list):
    """ Displays a QualysGuard report template list in an easy to copy/paste
    format.
    
    """
#    from lxml import objectify
    for template in list.REPORT_TEMPLATE:
#        print objectify.dump(template)
        print "[%s]\t{( %s | %s )}"%(template.ID,
                                     str(template.TEMPLATE_TYPE)[0],
                                     template.TITLE)

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
    
    # if requested, fetch and display report types 
    if options.listreports:
        qgc = build_v1_connector()
        ret = qgc.request("report_template_list.php")
        display_QG_report_template_list(QGXP_lxml_objectify(ret))
        
    elif options.launchrpt:
        if options.rpt_i != None:  # act differently if provided a list of IPs
            ret = qgs.request("report/",
                              "action=launch&template_id=%s&report_type=Scan&output_format=%s&report_refs=%s&report_title=%s&ips=%s"%
                              (options.rpt_n, options.rpt_o, options.rpt_r, options.rpt_t, options.rpt_i))
        else: # vs. not having a list of IPs
            ret = qgs.request("report/",
                              "action=launch&template_id=%s&report_type=Scan&output_format=%s&report_refs=%s&report_title=%s"%
                              (options.rpt_n, options.rpt_o, options.rpt_r, options.rpt_t))
        r = QGXP_lxml_objectify(ret)
        print r.RESPONSE.ITEM_LIST.ITEM.VALUE

    elif options.prog_n:
        ret = qgs.request("report/","action=list&id=%s&"%(options.prog_n))
        r = QGXP_lxml_objectify(ret)
        if r.RESPONSE.REPORT_LIST.REPORT.STATUS.STATE == 'Running':
            print "Waiting"
        elif r.RESPONSE.REPORT_LIST.REPORT.STATUS.STATE == 'Finished':
            print "Finished"
        else:
            print "Unknown"

    elif options.dl_n:
        ret = qgs.request("report/","action=fetch&id=%s&"%(options.dl_n))
        print ret
    
    qgs.disconnect()
