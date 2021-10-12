from twisted.internet.protocol import Factory
from backend.protocol import BackendServerProtocol
from typing import Callable, Optional, Tuple

class BackendServerFactory(Factory):
    protocol = BackendServerProtocol