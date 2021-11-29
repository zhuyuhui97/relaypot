import json

from relaypot.output import null

class Writer(null.Writer):
    def __init__(self) -> None:
        return

    def write(self, logentry):
        with open('file.json', 'a') as f:
            logentry['timestamp']=''
            f.write(json.dumps(logentry))
            f.write('\n')
            
