""" A set of utility functions for processing XML responses from QualysGuard.
Most (if not all) names in this module are named with the QGXP prefix.

QGXP_ -> QualysGuard XML Processor
"""
import logging
import xml.dom.minidom

from datetime import datetime

from lxml import etree, objectify

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011, University of Waterloo"
__license__ = "BSD-new"

def QGXP_hostlist_to_list(qgXML):
    """ Return a list of IPs pulled from a QualysGuard HOST LIST XML block.
    
    Keyword Arguments:
    qgXML -- A string representing an entire response from QualysGuard.
    """
    hosts = []
    parsed = xml.dom.minidom.parseString(qgXML)
    host_list = parsed.getElementsByTagName("IP")
    
    for host in host_list:
        hosts.append(host.childNodes[0].data)
            
    return hosts

def QGXP_lxml_objectify(qgXML):
    """ Processes an XML response from QualysGuard and Returns an easy to
    access python object containing the information.
    
    """
    tree = objectify.fromstring(qgXML)
    logging.debug(objectify.dump(tree))
    return tree

def QGXP_qgdt_to_datetime(qgdt):
    """ Takes a QualysGuard format datetime string (yyyy-mm-ddThh:mm:ssZ) and
    Returns a python datetime object.
    
    """
    QGDT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strptime(str(qgdt),QGDT_FORMAT)
