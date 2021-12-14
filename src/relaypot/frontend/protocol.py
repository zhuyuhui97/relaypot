from twisted.internet.protocol import Protocol
from twisted.python import failure
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from relaypot.frontend.util import top_service, create_endpoint_services
from relaypot.frontend.backend import BackendClientProtocol
from relaypot import utils


class FrontendProtocol(Protocol):
    _log_basename = 'FProto'

    def __init__(self) -> None:
        self._log = Logger(namespace=self._log_basename)
        super().__init__()

    def connectionMade(self):
        self.backend_host = utils.global_config['backend']['host']
        self.backend_port = utils.global_config['backend']['port']
        self.bproto = None
        self.buf_to_send = []
        self.host_addr = self.transport.getHost()
        self.peer_addr = self.transport.getPeer()
        self.setup_log_namespace()
        self._log.info("Got peer connection.")
        self.setup_backend()
        # set session info here

    def connectionLost(self, reason: failure.Failure):
        self._log.info("Lost peer connection. reason:{reason}", reason=reason)
        self.close_backend()
        # TODO Protocol call <pair>.transport.loseConnection() in self.connectionLost() may make self.connectionLost() called again.

    def dataReceived(self, data: bytes):
        self.to_backend(data)

    def setup_log_namespace(self):
        self._log.namespace = "{basename:<10} p{peer_addr}->f:{fproto_port}".format(
            basename=self._log_basename, 
            peer_addr=self.peer_addr.host, 
            fproto_port=str(self.host_addr.port))

    def setup_backend(self):
        point = TCP4ClientEndpoint(reactor, self.backend_host, self.backend_port, timeout=20)
        d = connectProtocol(point, BackendClientProtocol())
        d.addCallback(self.on_bproto_connected)
        d.addErrback(self.on_bproto_error)

    def on_bproto_connected(self, bproto):
        self._log.info('Got bproto {}.'.format(str(bproto)))
        self.set_bproto(bproto)

    def on_bproto_error(self, reason):
        self._log.error(
            'Failed to connect to backend, closing connection to client: {reason}', reason=reason)
        self.transport.loseConnection()

    def set_bproto(self, bproto):
        # Set bproto.fproto here in case of we lost track of bproto and cause memory leak
        self.bproto = bproto
        self.bproto.set_fproto(self)

    def close_backend(self):
        if self.bproto != None:
            self._log.info('Closing connection to backend.')
            self.bproto.transport.loseConnection()
            self.bproto = None

    def to_backend(self, buf):
        if self.bproto == None:
            self._log.info('Buffering bytes when bproto is not ready.')
            self.buf_to_send.append(buf)
        else:
            self.bproto.send_backend(buf)
