import json, os

from relaypot.output import null
from relaypot import utils


class Writer(null.Writer):

    @staticmethod
    def pre_init():
        if utils.global_config == None:
            # TODO raise another exception
            raise Exception
        Writer.config = utils.global_config['backend']['filelog']
        Writer.basedir = Writer.config['base']

    def __init__(self, sid: str) -> None:
        super().__init__(sid)
        self.filepath = os.path.join(Writer.basedir, sid+'.json')

    def write(self, logentry):
        with open(self.filepath, 'a') as f:
            logentry['timestamp'] = str(logentry['timestamp'])
            f.write(json.dumps(logentry))
            f.write('\n')
