import traceback
from pydoc import locate

from twisted.internet.protocol import Factory
from twisted.logger import Logger

from relaypot.backend.protocol import BackendServerProtocol
from relaypot import utils

class BackendServerFactory(Factory):
    protocol = BackendServerProtocol
