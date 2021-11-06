from twisted.internet.protocol import Factory
from backend.protocol import BackendServerProtocol
from typing import Callable, Optional, Tuple
from utils import global_config


class BackendServerFactory(Factory):
    protocol = BackendServerProtocol

    def __init__(self) -> None:
        self.agent_cls = self.get_agent_class

    def get_agent_class(self):
        klass = None
        try:
            self.agent_name = global_config['backend']['agent']
            klass = __import__('agent.'+self.agent_name).Agent
        except:
            klass = __import__('agent.dummmy').Agent
        return klass
