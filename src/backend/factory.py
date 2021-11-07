from twisted.internet.protocol import Factory
from backend.protocol import BackendServerProtocol
from typing import Callable, Optional, Tuple
import utils
from pydoc import locate


class BackendServerFactory(Factory):
    protocol = BackendServerProtocol

    def __init__(self) -> None:
        self.agent_cls = self.get_agent_class()

    def get_agent_class(self):
        klass = None
        try:
            self.agent_name = utils.global_config['backend']['agent']
            cls_name = 'agent.' + self.agent_name + '.Agent'
            klass = locate(cls_name)
        except Exception as e:
            klass = locate('agent.dummy.Agent')
        return klass
