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

    def __init__(self, sid: str, sess) -> None:
        super().__init__(sid, sess)
        self.filepath = os.path.join(Writer.basedir, sid+'.json')
        self.ofile = open(self.filepath, 'a')

    def write(self, logentry):
        logentry['timestamp'] = str(logentry['timestamp'])
        self.ofile.write(json.dumps(logentry))
        self.ofile.write('\n')

    def close(self):
        self.ofile.close()
