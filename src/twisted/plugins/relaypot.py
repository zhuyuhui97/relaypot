from threading import Thread

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.cred import portal
from twisted.application.service import IServiceMaker
from twisted.application import internet, service
from twisted.internet import reactor

import relaypot.factory
# from relaypot.options import cmd_opt
from relaypot.top_service import top_service
from relaypot.util import create_endpoint_services
import utils
from utils.config import load_option

from twisted.python import usage

class Options(usage.Options):
    optParameters = [
        ["port", "p", "2323", "The port number to listen on."],
        ["backend", "b", "pot-api.acg.wtf:6667", "The URL of backend."]
    ]

@implementer(IServiceMaker, IPlugin)
class MyServiceMaker(object):
    tapname = "relaypot"
    description = "Run this! It'll make your dog happy."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        self.topService = top_service
        application = service.Application("relaypot")
        self.topService.setServiceParent(application)
        self.initProtocol(options)
        return self.topService

    def initProtocol(self, options):
        utils.options = options
        factory = relaypot.factory.HoneypotFactory()  # TODO: Add here
        factory.tac = self
        # factory.portal = portal.Portal(None) # TODO: Add credentical here
        # factory.portal.registerChecker(None)
        listen_port = options['port']
        listen_endpoints = ["tcp:{}:interface=0.0.0.0".format(listen_port)]  # TODO: Add here
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
