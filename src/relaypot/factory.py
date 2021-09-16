from twisted.internet.protocol import Factory
from relaypot.protocol import FrontendProtocol
from typing import Callable, Optional, Tuple

class HoneypotFactory(Factory):
    protocol = FrontendProtocol
    # def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
    #     return MyProtocol(addr)

# class MyFactory(Factory):
#     def __init__(self):
#         self.users = {}  # maps user names to Chat instances

#     def buildProtocol(self, addr):
#         return MyProtocol()