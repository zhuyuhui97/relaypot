from twisted.internet import protocol
from twisted.python import failure

from relaypot.agent.base import BaseAgent


class Agent(BaseAgent):
    def __init__(self, fproto:protocol.Protocol):
        return None

    def on_init(self):
        return None

    def on_request(self, buf):
        return None

    def on_front_lost(self, reason: failure.Failure):
        return None

    def on_agent_lost(self):
        return None