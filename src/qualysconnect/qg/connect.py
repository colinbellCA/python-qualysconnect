
""" Module that contains classes for setting up connections to QualysGuard API
and requesting data from it.
"""
import urllib2
import cookielib
import logging

from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
from urllib2 import HTTPCookieProcessor

from qualysconnect import __version__ as VERSION

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2013, University of Waterloo"
__license__ = "BSD-new"

class QGConnector:
    """ Base class that provides common connection functionality for
    QualysConnect QualysGuard API.
    """
    def __init__(self, pAPIVer, pHost="qualysapi.qualys.com"):
        self._APIVersion = pAPIVer
        self._APIHost = pHost
        self._opener = None  # None reference stub for common 'request' handle
        
        # Based on the provided API Version number and hostname,
        # calculate the API URI that we should use to request from QualysGuard.
        if self._APIVersion == 1:   # connector to QualysGuard API v1
            self._APIURI = "https://%s/msp/"%(pHost,)
        elif self._APIVersion == 2:  #connector to QualysGuard API v2
            self._APIURI = "https://%s/api/2.0/fo/"%(pHost,)
        else:
            raise Exception("Unknown QualysGuard API Version Number (%s)"
                            %(self._APIVersion,))
        
        logging.info("Connecting to URI (%s) with APIv(%d)"%
                     (self._APIURI,self._APIVersion))

    def _generate_request(self,apiReq,data=None):
        """ Returns a urllib2.Request object for this connector's API URI and
        API Version combination.
        """
        headers = {"X-Requested-With":"uWaterloo QualysConnect (python) v%s"%(VERSION,)}
        req = urllib2.Request(''.join((self.apiURI(),apiReq)), data, headers)
        
        logging.info("GENREQ> %s"%(req.get_full_url(),))
        logging.debug("\t> w/ %s"%(data,))
        return req

    def apiURI(self):
        """ Return the base API URI calculated for this QualysGuard API version
        and hostname combination.
        """
        return self._APIURI

    def apiHOST(self):
        """ Returns the hostname of the Qualys instance this connector is talking
        to.
        """
        return self._APIHost

    def version(self):
        """ Return the API Version that this QualysGuard Connector (QGConnector)
        believes it is interacting with.
        """
        return self._APIVersion
    
    def build_request(self,apiReq,data=None):
        """ Build and return the HTTP opener to the QualysGuard API w/ the
        provided API request.
        
        Keyword Arguments:
        ==================
        apiReq -- request string from QualysGuard URL base onward.
        data -- [optional] if provided, use HTTP POST and submit data provided.
        """
        qualysRequest = self._generate_request(apiReq,data)
        logging.debug("QGC-build_request| %s, %s"%(str(apiReq), str(data)))
        request_opener = self._opener.open(qualysRequest)
        return request_opener
    
    def request(self, apiReq, data=None):
        """ Return the response from QualysGuard API for the provided request.
        
        Keyword Arguments:
        ==================
        apiReq -- request string from QualysGuard URL base onward.
        data -- [optional] if provided, use HTTP POST and submit data provided.
        """
        request = self.build_request(apiReq, data)
        return request.read()

class QGAPIConnect(QGConnector):
    """ Qualys Connection class which allows requests to the QualysGuard API
    using HTTP-Basic Authentication (over SSL).
    
    Notes:
    ======
    - Remote certificate verification is not supported.
    - This only currently functions with API v1 (not sure why).
    """
    def __init__(self, pUser, pPassword, pHost=None, pApiVer=1):

        # Handle special case: APIv2 does not work yet. Raise Exception early.
        if pApiVer is not 1:
            raise Exception("HTTP-Basic API Connector does not work with QG API\
                            version != 1.")

        # If provided a hostname, call base class with it.  Otherwise, use
        #  'default' hostname defined in QGConnector constructor.
        if not pHost:
            QGConnector.__init__(self, pApiVer) 
        else:
            QGConnector.__init__(self, pApiVer, pHost)

        # Setup password manager and HTTPBasicAuthHandler
        self._passman = HTTPPasswordMgrWithDefaultRealm()
        self._passman.add_password(None, self.apiURI(), pUser, pPassword)
        self._opener = urllib2.build_opener(HTTPBasicAuthHandler(self._passman))

class QGAPISession(QGConnector):
    """ Qualys Connection class which allows requests to the QualysGuard API
    using Session Authentication.

    Notes:
    ======
    - Remote certificate verification is not supported.
    """
    def __init__(self, pUser, pPassword, pHost=None):

        # If provided a hostname, call base class with it.  Otherwise, use
        #  'default' hostname defined in QGConnector constructor.
        if not pHost:
            QGConnector.__init__(self, 2) 
        else:
            QGConnector.__init__(self, 2, pHost)

        # Configure cookie handling and install capable 
        self._user = pUser;
        self._password = pPassword;
        self._cj = cookielib.CookieJar()
        self._opener = urllib2.build_opener(HTTPCookieProcessor(self._cj))
        #NOT-REQUIRED?# urllib2.install_opener(self._opener)

    def connect(self):
        """ Begin QualysGuard API Session (get session cookie). """
        return self.request("session/",
                            "action=login&username=%s&password=%s"
                               %(self._user,self._password))

    def disconnect(self):
        """ End QualysGuard API Session (invalidate session cookie). """
        return self.request("session/","action=logout")
