from twisted.application.internet import TCPClient
from twisted.internet.protocol import Factory, Protocol
from typing import Tuple

class UpstreamProtocol(Protocol):
    def __init__(self, down_prot) -> None:
        self.down_prot = down_prot
        super().__init__()
    def connectionMade(self):
        # return super().connectionMade()
        self.down_prot.set_upstream(self)
        pass
    def connectionLost(self, reason: failure.Failure):
        # return super().connectionLost(reason=reason)
        pass
    def dataReceived(self, data: bytes):
        self.down_prot.recv_upstream()
        # return super().dataReceived(data)

class UpstreamFactory(Factory):

    def __init__(self, down_prot) -> None:
        self.down_prot = down_prot
        super().__init__()

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        return super().buildProtocol(addr, self.down_prot)

class UpstreamClient(TCPClient):
    def __init__(self, down_prot, *args, **kwargs):
        self.down_prot = down_prot
        fup = UpstreamFactory(down_prot=down_prot)
        super().__init__(fup, *args, **kwargs)