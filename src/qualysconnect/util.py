""" A set of utility functions for QualysConnect module. """
import logging
import socket

import qualysconnect.config as qcconf
import qualysconnect.qg.connect as qcconn

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011, University of Waterloo"
__license__ = "BSD-new"

# define global values used by community code. will standardize debugging later.
package = 'qualysconnect'
module = 'util.py'
from . import __version__ as version

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

# ---
# BEYOND HERE lie deprecated dragons.  :-S
# ---
# IP checking and CIDR utilities built with ipaddr were submitted by a
#  community developer. In order to allow users to keep using the provided
#  scripts without having ipaddr as a dependency, I am performing a
#  deprecated import here.  This will break feature parity between users with
#  ipaddr installed and those without.
#
# Eventually, I will look to migrate to ipaddr ONLY code but I will leave this
#  as is for a few releases for the mental health of people who use the code
#  in locked down operational environments where ipaddr may be a non-trivial
#  addition to systems.
# ---
try:
    # BEGIN new 'ipaddr' aware code. If the module exists you'll get nice new magic.
    import ipaddr
    logging.warn('using ipaddr IP verification + CIDR utilities.')
    def is_valid_ip_address(address, version=None):
        """ Check validity of address
            Return True if 'address' is a valid ipv4 or ipv6 address.
        """
        # Validate version:
        if version:
            if not isinstance(version, int):
                raise TypeError('Version is not of type "int"')
                return False
            if not (version == 4 or version == 6):
                raise ValueError('IP version is set to an invalid number: %s' %
                                 version)
                return False
        try:
            ipaddr.IPAddress(address,version)
        except ValueError, e:
            logging.debug('%s/%s-%s, Error: %s' % (package,module,version,e))
            return False
        return True
    
    def is_valid_ipv4_address(address):
        """ Check validity of address
            Return True if 'address' is a valid ipv4 address.
        """
        return is_valid_ip_address(address,4)
    
    def is_valid_ipv6_address(address):
        """ Check validity of address
            Return True if 'address' is a valid ipv6 address.
        """
        return is_valid_ip_address(address,6)
    
    def is_valid_ip_range(iprange, version=None):
        """ Check validity of iprange
            Return True if 'iprange' is a range of ip addresses in a format that
            Qualys's API will accept (i.e. "startip-endip" where
            startip < endip).
        """
        # Validate version:
        if version:
            if not isinstance(version, int):
                raise TypeError('Version is not of type "int"')
                return False
            if not (version == 4 or version == 6):
                raise ValueError('IP version is set to an invalid number: %s' %
                                 version)
                return False
        
        try:
            (start_ip,end_ip) = iprange.split('-')
            if ipaddr.IPAddress(start_ip) == ipaddr.IPAddress(end_ip):
                logging.debug('%s/%s-%s, Error: %s' %
                              (package,module,version,
                               'Start and End IP Address in an IP Range can' \
                               'not be the same IP Address.'))
                return False
            # A valid range requires:
            # 1) The start_ip must be a valid ipv4 address.
            # 2) The end_ip must be a valid ipv4 address.
            # 3) The start_ip must be less than the end_ip.
            # Although socket operations are nice (as shown in the ipaddr free
            #  code in qualysconnect.util), it's not feasible to determine that the
            #  start_ip is less than the end_ip without considerable effort.
            # We'll use the ipaddr.summarize_address_range function to test all
            #  three at one time.
            ipaddr.summarize_address_range(ipaddr.IPAddress(start_ip,version),
                                           ipaddr.IPAddress(end_ip,version))
        except ipaddr.AddressValueError, e:
            logging.debug('%s/%s-%s, Error: %s' % (package,module,version,e))
            return False
        except ValueError, e:
            logging.debug('%s/%s-%s, Error: %s' % (package,module,version,e))
            return False
        return True
    
    def is_valid_ipv4_range(iprange):
        """ Check validity of iprange
            Return True if 'iprange' is a range of ipv4 addresses in a format
            that Qualys's API will accept (i.e. "startip-endip" where
            startip < endip).
        """
        return is_valid_ip_range(iprange,4)
    
    def is_valid_ipv6_range(iprange):
        """ Check validity of iprange
            Return True if 'iprange' is a range of ipv4 addresses in a format
            that Qualys's API will accept (i.e. "startip-endip" where
            startip < endip).
        """
        return is_valid_ip_range(iprange,6)
    
    def cidr_to_ip(cidr,version=None):
        """ Convert an ip address or ip range provided in cidr notation (either
        bitmask or netmask notation) to the ip address or ip range format that
        is accepted by Qualys's API. (e.g. cidr_to_ip('10.0.0.0/24') returns the
        string '10.0.0.0-10.0.0.255'.
            Returns a String containing an ip address or ip range that can be
            provided to the Qualys API. 
        """
        # Validate version:
        if version:
            if not isinstance(version, int):
                raise TypeError, 'Version is not of type "int"'
                return False
            if not (version == 4 or version == 6):
                raise ValueError, 'IP version is set to an invalid number: %s' % version
                return False
        try:
            cidr_net = ipaddr.IPNetwork(cidr,version)
        except ValueError, e:
            logging.debug('%s/%s-%s, Error: %s' % (package,module,version,e))
            raise ValueError, e
        if cidr_net[0] == cidr_net[-1]:
            return str(cidr_net[0])
        iprange = '%s-%s' % (cidr_net[0],cidr_net[-1])
        return iprange
    
    def cidr_to_ipv4(cidr):
        """ Convert an ipv4 address or ipv4 range provided in cidr notation
        (either bitmask or netmask notation) to the ip address or ip range
        format that is accepted by Qualys's API.
        (e.g. cidr_to_ip('192.0.2.0/24') returns the string
        '192.0.2.0-192.0.2.255'.
            Returns a String containing an ip address or ip range that can be
            provided to the Qualys API. 
        """
        return cidr_to_ip(cidr,4)
    
    def cidr_to_ipv6(cidr):
        """ Convert an ipv6 address or ipv6 range provided in cidr notation
        (either bitmask or netmask notation) to the ip address or ip range
        format that is accepted by Qualys's API. (e.g.
        cidr_to_ip('2001:db8::fff/120') returns the string
        '2001:db8::f00-2001:db8::fff'.
            Returns a String containing an ipv6 address or ipv6 range that can
            be provided to the Qualys API. 
        """
        return cidr_to_ip(cidr,4)
    
    def decode_ip_string(ipstring):
        """ Validates ipstring is in a format that can be provided to the Qualys
        API, if it is not in a format that can be accepted by the Qualys API, it
        attempts to put it in a format that is acceptable (e.g. converting cidr
        notation to the ip range notation that Qualys expects)
            Returns a string that is valid to hand to the 'ips' key in the
            Qualys API.
        """
        cml=[]
        ip_list = ipstring.split(',')
        # Should probably check for any repeated or overlapping IP addresses here,
        # but skipping for now.
        for i in ip_list:
            # This is a kludge, but I couldn't come up with a good way to make the
            # error report the string that generated the error, rather than the
            # potentially modified version of the string that caused the error.
            new_i=i 
            if '/' in i:
                new_i = cidr_to_ip(i)
            if (is_valid_ip_address(new_i) or is_valid_ip_range(new_i)):
                cml.append(new_i)
            else:
                raise ValueError("IP argument cannot be parsed, \'%s\' is not" \
                                 "a valid IP Range or IP Address" % i)
        return ",".join(cml)
except ImportError:
    # BEGIN deprecated - Rudimentary "non-ipaddr" IP utilities. 
    logging.warn("DEPRECATED: using simple IP utilities." \
                 "ipaddr will be required in the future.")
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
