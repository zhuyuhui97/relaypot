import datetime

class BaseLogger():
    def get_timestamp(self):
        # return datetime.datetime.utcnow().isoformat()
        return datetime.datetime.utcnow()