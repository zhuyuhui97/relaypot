from pydoc import locate
import traceback
from relaypot import utils

def get_agent_class():
    klass = None
    try:
        agent_name = utils.global_config['backend']['agent']
        cls_name = 'relaypot.agent.' + agent_name + '.Agent'
        klass = locate(cls_name)
        if klass == None:
            raise Exception
        # self._log.info('Loaded agent class {cls}', cls=cls_name)
        print('Loaded agent class {cls}'.format(cls=cls_name))
    except Exception as e:
        # self._log.info('Error loading agent class: {ex}, {trace}', ex=e, trace=traceback.format_exc())
        print('Error loading agent class: {ex}, {trace}'.format(ex=e, trace=traceback.format_exc()))
        klass = locate('relaypot.agent.dummy.Agent')
    return klass

def get_writer_class():
    klass = None
    try:
        agent_name = utils.global_config['backend']['agent']
        cls_name = 'relaypot.output.' + agent_name + '.Writer'
        klass = locate(cls_name)
        if klass == None:
            raise Exception
        # _log.info('Loaded writer class {cls}', cls=cls_name)
        print('Loaded writer class {cls}'.format(cls=cls_name))
    except Exception as e:
        # _log.info('Error loading writer class: {ex}, {trace}', ex=e, trace=traceback.format_exc())
        print('Error loading writer class: {ex}, {trace}'.format(ex=e, trace=traceback.format_exc()))
        klass = locate('relaypot.output.null.Writer')
    return klass