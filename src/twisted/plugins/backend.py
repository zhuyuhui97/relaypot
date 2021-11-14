from zope.interface import implementer
from twisted.plugin import IPlugin
from twisted.cred import portal
from twisted.application.service import IServiceMaker
from twisted.application import service
from twisted.internet import reactor
from twisted.python import usage

from relaypot.backend.factory import BackendServerFactory
from relaypot.frontend.top_service import top_service
from relaypot.frontend.util import create_endpoint_services
from relaypot.utils.config import load_option, load_git_rev
from relaypot import utils


class Options(usage.Options):
    optParameters = [
        ["config", "c", "config.yaml", "Config file"]
    ]


@implementer(IServiceMaker, IPlugin)
class MyServiceMaker(object):
    tapname = "relaypot-backend"
    description = "Run this! It'll make your dog happy."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        self.topService = top_service
        application = service.Application("relaypot-backend")
        self.topService.setServiceParent(application)
        # TODO Rewrite config loader
        utils.options = options
        load_option(options['config'])
        load_git_rev()
        self.initProtocol(options)
        return self.topService

    def initProtocol(self, options):
        factory = BackendServerFactory()  # TODO: Add here
        factory.tac = self
        # factory.portal = portal.Portal(None) # TODO: Add credentical here
        # factory.portal.registerChecker(None)
        # listen_port = options['port']
        listen_port = utils.global_config['backend']['port']
        listen_endpoints = ["tcp:{}:interface=0.0.0.0".format(
            listen_port)]  # TODO: Add here
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
