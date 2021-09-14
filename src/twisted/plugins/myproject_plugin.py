from threading import Thread

from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.cred import portal
from twisted.application.service import IServiceMaker
from twisted.application import internet, service
from twisted.internet import reactor

import relaypot.factory
from relaypot.top_service import top_service
from relaypot.util import create_endpoint_services

class Options(usage.Options):
    optParameters = [["port", "p", 1235, "The port number to listen on."]]



@implementer(IServiceMaker, IPlugin)
class MyServiceMaker(object):
    tapname = "relaypot"
    description = "Run this! It'll make your dog happy."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        # self.topService = service.MultiService()
        self.topService = top_service
        application = service.Application("relaypot")
        self.topService.setServiceParent(application)
        # return internet.TCPServer(int(options["port"]), relaypot.factory.MyFactory())
        self.initProtocol()
        return self.topService

    def initProtocol(self):
        factory = relaypot.factory.MyFactory() # TODO: Add here
        factory.tac = self
        #factory.portal = portal.Portal(None) # TODO: Add credentical here
        #factory.portal.registerChecker(None)
        listen_endpoints = "tcp:2324:interface=0.0.0.0".split() # TODO: Add here
        create_endpoint_services(
            reactor,
            self.topService,
            listen_endpoints,
            factory
        )



# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.
serviceMaker = MyServiceMaker()