from twisted.application.internet import TCPClient
from twisted.python import log, failure, components
from twisted.internet.protocol import ClientFactory, Protocol
from typing import Tuple
import json


class BackendClientProtocol(Protocol):

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
        self.transport.write(self.encode_info())

    def connectionLost(self, reason: failure.Failure):
        super().connectionLost(reason=reason)
        self.frontend.transport.loseConnection()
        pass

    def dataReceived(self, data: bytes):
        encoded = self.encode_buf(data)
        self.frontend.transport.write(encoded)
        # return super().dataReceived(data)

    def send_backend(self, buf):
        self.transport.write(self.encode_buf(buf))

    def encode_info(self):
        obj = {
            'dest_ip': self.factory.host_addr.host,
            'dest_port': self.factory.host_addr.port,
            'src_ip': self.factory.peer_addr.host,
            'src_port': self.factory.peer_addr.port,
        }
        return json.dumps(obj).encode() + b'\r\n'

    def encode_buf(self, buf):
        escaped_buf = repr(buf)
        obj = {
            'length': len(buf),
            'hashsum': '',
            'buf': escaped_buf
        }
        return json.dumps(obj, ensure_ascii=False).encode()+b'\r\n'
        # TODO


class BackendClientFactory(ClientFactory):

    def __init__(self, frontend) -> None:
        self.frontend = frontend
        super().__init__()

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        return BackendClientProtocol(self, self.frontend)


class UpstreamClient(TCPClient):
    def __init__(self, down_prot, *args, **kwargs):
        self.down_prot = down_prot
        fup = BackendClientFactory(frontend=down_prot)
        super().__init__(fup, *args, **kwargs)
