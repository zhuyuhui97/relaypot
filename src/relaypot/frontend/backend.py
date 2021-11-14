from typing import Tuple
import json

from twisted.python import failure
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.logger import Logger


class BackendClientProtocol(Protocol):

    _log_basename = 'BCliProto'

    def __init__(self, factory, fproto) -> None:
        self._log = Logger()
        self.factory = factory
        self.fproto = fproto
        self.peer_addr = fproto.peer_addr
        self.host_addr = fproto.host_addr
        super().__init__()

    def connectionMade(self):
        self.back_addr = self.transport.getPeer()
        self.setup_log_namespace()
        self._log.info('Made backend connection {bhost}:{port}.',
                       bhost=self.back_addr.host, port=self.back_addr.port)
        self.transport.write(self.encode_info())  # TODO
        if len(self.fproto.buf_to_send) != 0:
            self._log.info('Sending {} buffered bytes.'.format(
                str(len(self.fproto.buf_to_send))))
            for buf in self.fproto.buf_to_send:
                self.send_backend(buf)
            self.fproto.buf_to_send.clear()

    def connectionLost(self, reason: failure.Failure):
        self._log.info('Lost backend connection {bhost}:{port}. reason:{reason}',
                       bhost=self.back_addr.host, 
                       port=self.back_addr.port, 
                       reason=reason)
        super().connectionLost(reason=reason)
        self.fproto.transport.loseConnection()
        # TODO Protocol call <pair>.transport.loseConnection() in self.connectionLost() may make self.connectionLost() called again.

    def dataReceived(self, data: bytes):
        self.fproto._log.info('p <- f -- {buf}', buf=data)
        self.fproto.transport.write(data)

    def send_backend(self, buf):
        self.fproto._log.info('p -> f -- {buf}', buf=buf)
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

    def setup_log_namespace(self):
        self._log.namespace = "{basename:<10} p{peer_addr}->f:{fproto_port}->b{bproto_addr}:{bproto_port}".format(
            basename=self._log_basename,
            peer_addr=self.peer_addr.host,
            fproto_port=str(self.host_addr.port),
            bproto_addr=self.back_addr.host,
            bproto_port=self.back_addr.port)


class BackendClientFactory(ClientFactory):

    def __init__(self, fproto) -> None:
        self.fproto = fproto
        super().__init__()

    def buildProtocol(self, addr: Tuple[str, int]) -> "Protocol":
        return BackendClientProtocol(self, self.fproto)
