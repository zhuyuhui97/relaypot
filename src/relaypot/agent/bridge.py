from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.python import failure
from twisted.logger import Logger

from relaypot.agent.base import BaseAgent


class BridgeProtocol(protocol.Protocol):

    def __init__(self, agent, log) -> None:
        self._log = log
        self.agent = agent

    def dataReceived(self, data: bytes):
        self.agent.fproto.send_response([data])

    def connectionLost(self, reason: failure.Failure):
        self.agent.on_agent_lost()


class Agent(BaseAgent):
    _log_basename = 'Bridge_Agent'

    def __init__(self, fproto: protocol.Protocol):
        self._log = Logger(namespace=self._log_basename)
        self.fproto = fproto
        self.bproto = None
        self.buf_to_send = []
        # TODO make it NOT hard coded
        point = TCP4ClientEndpoint(reactor, "localhost", 2324)
        d = connectProtocol(point, BridgeProtocol(self, self._log))
        d.addCallback(self.on_back_connected)
        d.addErrback(self.on_back_failed)

    def on_back_connected(self, proto):
        self.bproto = proto
        if len(self.buf_to_send) > 0:
            for item in self.buf_to_send:
                self.bproto.transport.write(item)
            self.buf_to_send.clear()

    def on_back_failed(self):
        self._log.error('ASD')
        self.fproto.transport.loseConnection()

    def on_init(self):
        return None

    def on_request(self, buf):
        if self.bproto == None:
            print('buffering buf')
            self.buf_to_send.append(buf)
        else:
            self.bproto.transport.write(buf)

    def on_front_lost(self, reason: failure.Failure):
        if self.bproto != None:
            self.bproto.transport.loseConnection()

    def on_agent_lost(self):
        self.fproto.transport.loseConnection()