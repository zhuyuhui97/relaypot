from twisted.internet.protocol import Factory
from relaypot.protocol import MyProtocol
from typing import Callable, Optional, Tuple

class MyFactory(Factory):
    protocol = MyProtocol
    # def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
    #     return MyProtocol(addr)

# class MyFactory(Factory):
#     def __init__(self):
#         self.users = {}  # maps user names to Chat instances

#     def buildProtocol(self, addr):
#         return MyProtocol()