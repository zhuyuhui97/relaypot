from twisted.internet.protocol import Factory

from relaypot.frontend.protocol import FrontendProtocol

class HoneypotFactory(Factory):
    protocol = FrontendProtocol
