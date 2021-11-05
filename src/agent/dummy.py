from agent.base import BaseAgent


class DummyAgent(BaseAgent):
    def __init__(self):
        return None

    def on_init(self):
        return None

    def on_request(self, buf):
        return None
