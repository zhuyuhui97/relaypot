from twisted.internet.protocol import Factory
from relaypot.protocol import FrontendProtocol

class HoneypotFactory(Factory):
    protocol = FrontendProtocol
