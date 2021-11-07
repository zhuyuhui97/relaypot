from twisted.internet import protocol
from twisted.python import failure


class BaseAgent():
    def __init__(self, fproto:protocol.Protocol):
        raise NotImplementedError

    def on_init(self):
        raise NotImplementedError

    def on_request(self, buf):
        raise NotImplementedError

    def on_front_lost(self, reason: failure.Failure):
        return None

    def on_agent_lost(self):
        return None
