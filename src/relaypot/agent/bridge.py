from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.python import failure
from twisted.logger import Logger

from relaypot.agent.base import BaseAgent


class BridgeProtocol(protocol.Protocol):

    def __init__(self, agent: BaseAgent, log) -> None:
        self._log = log
        self.agent = agent

    def dataReceived(self, data: bytes):
        self.agent.on_response(data)

    def connectionLost(self, reason: failure.Failure):
        self.agent.on_agent_lost()


class Agent(BaseAgent):
    _log_basename = 'Bridge_Agent'
    REQ_USERNAME = b'login:'
    REQ_PASSWORD = b'Password:'
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3

    def __init__(self, fproto: protocol.Protocol):
        self.STATUS = self.STATUS_NO_AUTH
        self._log = Logger(namespace=self._log_basename)
        self.fproto = fproto
        self.bproto = None
        self.buf_to_send = []
        # TODO make it NOT hard coded
        point = TCP4ClientEndpoint(reactor, "192.168.50.1", 23)
        d = connectProtocol(point, BridgeProtocol(self, self._log))
        d.addCallback(self.on_back_connected)
        d.addErrback(self.on_back_failed)

    def on_back_connected(self, proto):
        self.bproto = proto
        if len(self.buf_to_send) > 0:
            for item in self.buf_to_send:
                self._to_backend(item)
            self.buf_to_send.clear()

    def on_back_failed(self):
        self._log.error('ASD')
        self.fproto.transport.loseConnection()

    def on_request(self, buf):
        # TODO Process \xff
        if self.STATUS == self.STATUS_REQ_USERNAME:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                buf = b'admin\r\n'
            else:
                return
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                buf = b'123123\r\n'
            else:
                return
        if self.bproto == None:
            print('buffering buf')
            self.buf_to_send.append(buf)
        else:
            self._to_backend(buf)

    def on_response(self, buf: bytes):
        self.set_status(buf)
        self._to_frontend([buf])

    def on_front_lost(self, reason: failure.Failure):
        if self.bproto != None:
            self.bproto.transport.loseConnection()

    def _to_backend(self, buf: bytes):
        self.bproto.transport.write(buf)

    def set_status(self, buf):
        if self.STATUS == self.STATUS_NO_AUTH and self.REQ_USERNAME in buf:
            self.STATUS = self.STATUS_REQ_USERNAME
        elif self.STATUS == self.STATUS_REQ_USERNAME and self.REQ_PASSWORD in buf:
            self.STATUS = self.STATUS_REQ_PASSWORD
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            self.STATUS = self.STATUS_AUTH_DONE
