from twisted.internet.protocol import Factory
from relaypot.protocol import FrontendProtocol
from typing import Callable, Optional, Tuple

class HoneypotFactory(Factory):
    protocol = FrontendProtocol
