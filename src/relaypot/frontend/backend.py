from typing import Tuple
import json

from twisted.python import failure
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.logger import Logger


class BackendClientProtocol(Protocol):
    
    twlog = Logger()
    
    def __init__(self, factory, fproto) -> None:
        self.factory = factory
        self.fproto = fproto
        self.peer_addr = fproto.peer_addr
        self.host_addr = fproto.host_addr
        super().__init__()

    def connectionMade(self):
        self.back_addr = self.transport.getPeer()
        self.twlog.info('Made backend connection {bhost}:{port}.', bhost=self.back_addr.host, port=self.back_addr.port)
        self.transport.write(self.encode_info()) # TODO
        if len(self.fproto.buf_to_send) != 0:
            self.twlog.info('Sending {} buffered bytes.'.format(str(len(self.fproto.buf_to_send))))
            for buf in self.fproto.buf_to_send:
                self.send_backend(buf)
            self.fproto.buf_to_send.clear()

    def connectionLost(self, reason: failure.Failure):
        self.twlog.info('Lost backend connection {bhost}:{port}.', bhost=self.back_addr.host, port=self.back_addr.port)
        super().connectionLost(reason=reason)
        self.fproto.transport.loseConnection()

    def dataReceived(self, data: bytes):
        self.twlog.info('{peer_addr} <- :{fproto_port} -- {buf}', peer_addr=self.peer_addr.host, fproto_port=str(self.host_addr.port), buf=data)
        self.fproto.transport.write(data)

    def send_backend(self, buf):
        self.twlog.info('{peer_addr} -> :{fproto_port} -- {buf}', peer_addr=self.peer_addr.host, fproto_port=str(self.host_addr.port), buf=buf)
        self.transport.write(self.encode_buf(buf))

    def encode_info(self):
        obj = {
            'dest_ip': self.host_addr.host,
            'dest_port': self.host_addr.port,
            'src_ip': self.peer_addr.host,
            'src_port': self.peer_addr.port,
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

    def __init__(self, fproto) -> None:
        self.fproto = fproto
        super().__init__()

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        return BackendClientProtocol(self, self.fproto)