import os, random
class TelnetInteractor():
    STATUS_REQ_USERNAME = 0
    STATUS_REQ_PASSWORD = 1
    STATUS_REQ_COMMAND = 2
    
    def __init__(self, profile_name=None, profile_base='profiles'):
        plist = os.listdir()
        if profile_name ==None:
            rnd = random.randrange(0, len(plist))
            self.profile_name = plist[rnd]
        else:
            self.profile_name = profile_name
        self.profile_base = profile_base
        self.status = self.STATUS_REQ_USERNAME

    def load_profile(self):
        filepath = os.path.join(self.profile_base, self.profile_name)
        with open(filepath) as pfile:
            self.banner = eval(pfile.readline())
            self.username_hint = eval(pfile.readline())
            self.password_hint = eval(pfile.readline())
            self.ps = eval(pfile.readline())
            while True:
                line = pfile.readline()
                if line == '':
                    break
    
    def send_init(self):
        return [self.banner, self.username_hint]

    def got_buffer(self, buf):
        if self.status==self.STATUS_REQ_USERNAME:
            self.status = self.STATUS_REQ_PASSWORD
            return [self.password_hint]
        elif self.status==self.STATUS_REQ_PASSWORD:
            self.status = self.STATUS_REQ_COMMAND
            return [self.ps]
        else:
            return [self.get_resp(buf), '\n', self.ps]

    def get_resp(self, buf):
        return 'sh: command not found: '+ buf.split()[0]

