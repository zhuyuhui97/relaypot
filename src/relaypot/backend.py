from twisted.application.internet import TCPClient
from twisted.python import log, failure, components
from twisted.internet.protocol import ClientFactory, Protocol
from typing import Tuple

class BackendProtocol(Protocol):


    def __init__(self, factory, frontend) -> None:
        self.factory = factory
        self.frontend = frontend
        super().__init__()
    def connectionMade(self):
        # return super().connectionMade()
        self.frontend = self.factory.frontend
        if len(self.frontend.buf_to_send) != 0:
            for buf in self.frontend.buf_to_send:
                self.send_backend(buf)
        self.frontend.set_backend_prot(self)

    def connectionLost(self, reason: failure.Failure):
        super().connectionLost(reason=reason)
        self.frontend.transport.loseConnection()
        pass
    def dataReceived(self, data: bytes):
        self.frontend.transport.write(data)
        # return super().dataReceived(data)

    def send_backend(self, buf):
        self.transport.write(self.encode_buf(buf))

    def encode_buf(self, buf):
        return buf
        #TODO
        

class BackendFactory(ClientFactory):

    def __init__(self, frontend) -> None:
        self.frontend = frontend
        super().__init__()

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        return BackendProtocol(self, self.frontend)

class UpstreamClient(TCPClient):
    def __init__(self, down_prot, *args, **kwargs):
        self.down_prot = down_prot
        fup = BackendFactory(frontend=down_prot)
        super().__init__(fup, *args, **kwargs)