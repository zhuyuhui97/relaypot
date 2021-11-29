from twisted.internet import protocol
from twisted.python import failure


class BaseAgent():
    
    @staticmethod
    def pre_init():
        return

    def __init__(self, fproto: protocol.Protocol):
        self.fproto = fproto

    def on_init(self):
        return None

    def on_request(self, buf):
        raise NotImplementedError

    def on_response(self, buf_seq: list):
        '''
        Do nothing, just send to frontend.
        '''
        self._to_frontend(buf_seq)

    def on_front_lost(self, reason: failure.Failure):
        return None

    def on_agent_lost(self):
        # TODO Mark reason of loseConnection here!
        self.fproto.transport.loseConnection()

    def _to_backend(self, buf: bytes):
        raise NotImplementedError

    def _to_frontend(self, buf_seq: list):
        self.fproto.send_response(buf_seq)
