from twisted.internet.protocol import Factory
from twisted.logger import Logger
from backend.protocol import BackendServerProtocol
from typing import Callable, Optional, Tuple
import utils
import traceback
from pydoc import locate


class BackendServerFactory(Factory):
    protocol = BackendServerProtocol
    twlog = Logger()

    def __init__(self) -> None:
        self.agent_cls = self.get_agent_class()

    def get_agent_class(self):
        klass = None
        try:
            self.agent_name = utils.global_config['backend']['agent']
            cls_name = 'agent.' + self.agent_name + '.Agent'
            klass = locate(cls_name)
            self.twlog.info('Loaded agent class {cls}', cls=cls_name)
        except Exception as e:
            self.twlog.info('Error loading agent class: {ex}, {trace}', ex=e, trace=traceback.print_exc())
            klass = locate('agent.dummy.Agent')
        return klass
