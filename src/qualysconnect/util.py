""" A set of utility functions for QualysConnect module. """
import logging
import socket

import qualysconnect.config as qcconf
import qualysconnect.qg.connect as qcconn

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011, University of Waterloo"
__license__ = "BSD-new"

def build_v1_connector():
    """ Return a QGAPIConnect object for v1 API pulling settings from config
    file.
    """
    conf = qcconf.QualysConnectConfig()
    connect = qcconn.QGAPIConnect(conf.get_username(),
                                  conf.get_password(),
                                  conf.get_hostname())
    logging.info("Finished building v1 Connector.")
    return connect

def build_v2_session():
    """ Return a QGAPISession object for v2 API pulling settings for config
    file.
    """
    conf = qcconf.QualysConnectConfig()
    connect = qcconn.QGAPISession(conf.get_username(),
                                  conf.get_password(),
                                  conf.get_hostname())
    logging.info("Finished building v2 Connector.")
    return connect

def is_valid_ipv4_address(address):
    """ Check validity of address as a ipv4 address.
    Return True if 'address' is potentially a valid ipv4 address.
    """
    try:
        test_addr = socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # inet_pton not available
        try:
            test_addr = socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3  # verifies address was IPv4 dotted dec
    except socket.error: # attempt to create a socket failed. INVALID IPv4
        return False

    return True

def is_valid_ipv6_address(address):
    """ Check validity of address as a ipv6 address.
    Return True if 'address' is potentially a valid ipv6 address.
    """
    try:
        test_addr = socket.inet_pton(socket.AF_INET6, address)
    except socket.error: # attempt to create a socket failed.  INVALID IPv6
        return False
    return True

def is_valid_ip_address(address):
    """ Check validity of address as either an ipv4 or ipv6 address.
    Return True if 'address' is potentially a valid ip address.
    """
    if is_valid_ipv4_address(address) or is_valid_ipv6_address(address):
        return True
    else:
        return False

def hostname_to_ip(hostname):
    """ Takes a hostname and returns the corresponding IP address. """
    
    # simplify request.  ask for a simple TCP socket to http.  we only want IP
    addrinfo = socket.getaddrinfo(hostname, 'http')
    
    logging.debug('getaddrinfo returned %s'%(addrinfo,))
    
    family, socktype, proto, canonname, sockaddr = addrinfo[0]
    
    if family == socket.AF_INET:  # ipv4 sockaddr return is a 2-tuple
        return sockaddr[0]
    elif family == socket.AF_INET6: # ipv6 sockaddr return is a 4-tuple
        return sockaddr[0]
    else:
        raise Exception("Could not determine IP associated w/ %s"%(hostname,))
