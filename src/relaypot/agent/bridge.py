import hashlib, random
from urllib.parse import urlparse

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.python import failure
from twisted.logger import Logger

from relaypot.agent.base import BaseAgent
from relaypot import utils


class BridgeProtocol(protocol.Protocol):

    def __init__(self, agent: BaseAgent, log) -> None:
        self._log = log
        self.agent = agent

    def dataReceived(self, data: bytes):
        self.agent.on_response(data)

    def connectionLost(self, reason: failure.Failure):
        self.agent.on_agent_lost()
        # HACK Dereference manually to avoid memory leak
        self.agent = None


class Agent(BaseAgent):
    _log_basename = 'Bridge_Agent'
    REQ_USERNAME = b'login:'
    REQ_PASSWORD = b'Password:'
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3

    @staticmethod
    def pre_init():
        Agent.config = utils.global_config['backend']['bridge']
        Agent.pool = Agent.config['pool']

    def __init__(self, fproto: protocol.Protocol):
        self.STATUS = self.STATUS_NO_AUTH
        self._log = Logger(namespace=self._log_basename)
        self.fproto = fproto
        self.bproto = None
        self.buf_to_send = []
        self._req_frag = None
        self._resp_frag = None
        # TODO make it NOT hard coded
        # point = TCP4ClientEndpoint(reactor, "127.0.0.1", 2324)
        self.back_device = random.choice(Agent.pool)
        self._log.info('Selected backend device {device}', device=self.back_device)
        self.parse_pool_str(self.back_device)
        point = TCP4ClientEndpoint(reactor, self.point[0], int(self.point[1]))
        # BUG CROSS REFERENCE MAY CAUSE MEMORY LEAK
        d = connectProtocol(point, BridgeProtocol(self, self._log))
        d.addCallback(self.on_back_connected)
        d.addErrback(self.on_back_failed)
    
    def parse_pool_str(self, pstr:str):
        _pstr = pstr.split('@')
        self.cred = _pstr[0].split(':')
        self.point = _pstr[1].split(':')

    def get_info(self):
        return self.back_device

    def on_back_connected(self, proto):
        self.bproto = proto
        if len(self.buf_to_send) > 0:
            for item in self.buf_to_send:
                self._to_backend(item)
            self.buf_to_send.clear()

    def on_back_failed(self, reason):
        self._log.error('Failed connecting to backend device. reason={reason}', reason = reason)
        self.fproto.transport.loseConnection()
        # HACK Dereference manually to avoid memory leak
        self.fproto = None

    def on_request(self, buf):
        self.truncate_response(buf)
        # TODO Process \xff
        if self.STATUS == self.STATUS_REQ_USERNAME:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                buf = self.cred[0].encode() + b'\r\n'
            else:
                return
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                buf = self.cred[1].encode() + b'\r\n'
            else:
                return
        if self.bproto == None:
            print('buffering buf')
            self.buf_to_send.append(buf)
        else:
            self._to_backend(buf)

    def on_response(self, buf: bytes):
        self.truncate_request(buf)
        self.set_status(buf)
        self._to_frontend([buf])

    def on_front_lost(self, reason: failure.Failure):
        if self.bproto != None:
            self.bproto.transport.loseConnection()
        # HACK Dereference manually to avoid memory leak
        self.bproto = None
        self.fproto = None

    def _to_backend(self, buf: bytes):
        self.bproto.transport.write(buf)

    def set_status(self, buf):
        if self.STATUS == self.STATUS_NO_AUTH and self.REQ_USERNAME in buf:
            self.STATUS = self.STATUS_REQ_USERNAME
        elif self.STATUS == self.STATUS_REQ_USERNAME and self.REQ_PASSWORD in buf:
            self.STATUS = self.STATUS_REQ_PASSWORD
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            self.STATUS = self.STATUS_AUTH_DONE

    def truncate_request(self, new_resp_buf):
        if self._req_frag != None:
            self._log.info('TRUNK '+ repr(self._req_frag))
            self._log.info(hashlib.md5(self._req_frag).hexdigest())
            self._req_frag = None
        if self._resp_frag == None:
            self._resp_frag = new_resp_buf
        else:
            self._resp_frag = self._resp_frag + new_resp_buf


    def truncate_response(self, new_req_buf):
        if self._resp_frag != None:
            self._log.info('TRUNK '+ repr(self._resp_frag))
            self._log.info(hashlib.md5(self._resp_frag).hexdigest())
            self._resp_frag = None
        if self._req_frag == None:
            self._req_frag = new_req_buf
        else:
            self._req_frag = self._req_frag + new_req_buf
