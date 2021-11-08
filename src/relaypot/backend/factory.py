import traceback
from pydoc import locate

from twisted.internet.protocol import Factory
from twisted.logger import Logger

from relaypot.backend.protocol import BackendServerProtocol
from relaypot import utils

class BackendServerFactory(Factory):
    protocol = BackendServerProtocol
    _log_basename = 'BSrvFactory'
    

    def __init__(self) -> None:
        self._log = Logger(namespace=self._log_basename)
        self.agent_cls = self.get_agent_class()

    def get_agent_class(self):
        klass = None
        try:
            self.agent_name = utils.global_config['backend']['agent']
            cls_name = 'relaypot.agent.' + self.agent_name + '.Agent'
            klass = locate(cls_name)
            self._log.info('Loaded agent class {cls}', cls=cls_name)
        except Exception as e:
            self._log.info('Error loading agent class: {ex}, {trace}', ex=e, trace=traceback.format_exc())
            klass = locate('relaypot.agent.dummy.Agent')
        return klass
