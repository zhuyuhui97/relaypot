from twisted.internet import protocol
from twisted.python import failure

from relaypot.agent.base import BaseAgent


class Agent(BaseAgent):
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3
    
    def __init__(self, fproto:protocol.Protocol):
        self.fproto = fproto
        return None

    def on_init(self):
        self.on_response([b'\xff\xfd\x01\xff\xfd\x1f\xff\xfb\x01\xff\xfb\x03', b'R6300V2-14EF login: '])

    # def on_request(self, buf):
    #     if buf==b'/bin/busybox ECCHI\r\n':
    #         return [b'ECCHI: applet not found\r\n>']
    #     if buf==b'\r\n':
    #         return [b'\r\n> ']
    #     if buf==b'/bin/busybox ps; /bin/busybox ECCHI\r\n':
    #         return [b'PID USER       VSZ STAT COMMAND\r\n    115 yjsp     514 S    /1919/810', b'ECCHI: applet not found\r\n>']
    #     if buf==b'/bin/busybox cat /proc/mounts; /bin/busybox ECCHI\r\n':

    #         return [b'ECCHI: applet not found\r\n>']
    #     if buf.startswith(b'/bin/busybox echo -e \'\\x6b\\x61\\x6d\\x69/dev\''):
    #         return [b'kami/tmp',b'ECCHI: applet not found\r\n>']
    #     return [b'R6300V2-14EF login: ']

    def on_request(self, buf):
        blist = []
        if buf==b'\r\n':
            blist = [b'\r\n> ']
        elif buf==b'/bin/busybox ps; /bin/busybox ECCHI\r\n':
            blist = [b'PID USER       VSZ STAT COMMAND\r\n    115 yjsp     514 S    /1919/810', b'ECCHI: applet not found\r\n>']
        elif buf==b'/bin/busybox cat /proc/mounts; /bin/busybox ECCHI\r\n':

            blist = [b'ECCHI: applet not found\r\n>']
        elif buf.startswith(b'/bin/busybox echo -e \'\\x6b\\x61\\x6d\\x69/dev\''):
            blist = [b'kami/tmp']
        elif b'/bin/busybox cat /bin/echo\r\n' in buf:
            blist = [b'x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00(\x00\x01\x00\x00\x00D\xca\x00\x004\x00\x00\x00PX\x07\x00\x02\x00\x00\x054\x00 \x00\x06\x00(\x00\x19\x00\x18\x00\x06\x00\x00\x004\x00\x00\x004\x80\x00\x004\x80\x00\x00\xc0\x00\x00\x00\xc0\x00\x00\x00\x05\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\xf4\x00\x00\x00\xf4\x80\x00\x00\xf4\x80\x00\x00\x14\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\xbcF\x07\x00\xbcF\x07\x00\x05\x00\x00\x00\x00\x80\x00\x00\x01\x00\x00\x00\xbcF\x07\x00\xbcF\x08\x00\xbcF\x08\x00\x99\x10\x00\x00l\x16\x00\x00\x06\x00\x00\x00\x00\x80\x00\x00\x02\x00\x00\x00\xb0P\x07\x00\xb0P\x08\x00\xb0P\x08\x00\x08\x01\x00\x00\x08\x01\x00\x00\x06\x00\x00\x00\x04\x00\x00\x00Q\xe5td\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x04\x00\x00\x00/lib/ld-uClibc.so.0\x00\x07\x01\x00\x00b\x01\x00\x00\xda\x00\x00\x000\x01\x00\x00(\x01\x00\x009\x01\x00\x00?\x00\x00\x00\x00\x00\x00\x00a\x01\x00\x00\x04\x01\x00\x00L\x00\x00\x00\x9e\x00\x00\x00O\x01\x00\x00\xc7\x00\x00\x002\x01\x00\x00\x94\x00\x00\x00>\x00\x00\x00+\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x88\x00\x00\x00\xc4\x00\x00\x00P\x00\x00\x00[\x00\x00\x00T\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xed\x00\x00\x00    \x00\x00\x00\x00\x00\x00\x00b\x00\x00\x00}\x00\x00\x00\x00\x00\x00\x004\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00\'\x01\x00\x00#\x00\x00\x00\x00\x00\x00\x00.\x01\x00\x00\x12\x01\x00\x00\x06\x01\x00\x00)\x00\x00\x00=\x01\x00\x00\xff\xff\x00\x00\x00Y\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\xde\x00\x00\x00\xbf\x00\x00\x00\x00\x00\x00\x00\xef\x00\x00\x005\x00\x00\x008\x01\x00\x00\x00\x00\x00\x00?\x01\x00\x00\x00\x00\x00\x00\xe7\x00\x00\x00\xd1\x00\x00\x00\x14\x01\x00\x00\xd9\x00\x00\x00\xe8\x00\x00\x007\x00\x00\x00Q\x01\x00\x00D\x01\x00\x00U\x00\x00\x00f\x00\x00\x004\x01\x00\x00n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xeb\x00\x00\x00R\x01\x00\x00E\x01\x00\x00\x1d\x01\x00\x00\x0f\x01\x00\x00\x1a\x01\x00\x00\xca\x00\x00\x00\xd3\x00\x00\x00\x95\x00\x00\x00\x81\x00\x00\x00\x03\x01\x00\x00\x1d\x00\x00\x00B\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd7\x00\x00\x00\xdb\x00\x00\x00\xf2\x00\x00\x00\x90\x00\x00\x00\x15\x00\x00\x00\x00\x00\x00\x00:\x01\x00\x00\x8a\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9a\x00\x00\x00\x00\x00\x00\x00G\x01\x00\x00    \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\x00\x00\x00w\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>\x01\x00\x00\xc5\x00\x00\x00Q\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x84\x00\x00\x001\x01\x00\x00X\x01\x00\x00\xf3\x00\x00\x00\xd6\x00\x00\x00\x99\x00\x00\x00\xc1\x00\x00\x00\x00\x00\x00\x00<\x00\x00\x00\x00\x00\x00\x00\xe1\x00\x00\x007\x01\x00\x00\xf8\x00\x00\x00\xee\x00\x00\x00\xd4\x00\x00\x00\x19\x01\x00\x00\x00\x00\x00\x00\xd0\x00\x00\x00\xe9\x00\x00\x00Z\x01\x00\x00\x02\x01\x00\x00\xe4\x00\x00\x00\x00\x00\x00\x00\xb1\x00\x00\x00;\x00\x00\x00J\x01\x00\x00\x0b\x01\x00\x00\x00\x00\x00\x00\"\x01\x00\x006\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00d\x00\x00\x00\x82\x00\x00\x00\x00\x00\x00\x00\xfd\x00\x00\x00F\x01\x00\x00-\x01\x00\x00T\x00\x00\x00\x00\x00\x00\x00O\x00\x00\x00\x00\x00\x00\x00N\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00[\x01\x00\x00\x13\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9\x00\x00\x00X\x00\x00\x00\x86\x00\x00\x00\xb6\x00\x00\x00\x04\x00\x00\x00\xfe\x00\x00\x00`\x01\x00\x00\x00\x00\x00\x00K\x01\x00\x00\x00\x00\x00\x00\xe2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00A\x01\x00\x00\xb0\x00\x00\x00^\x01\x00\x00\x00\x00\x00\x00\xaa\x00\x00\x00\x11\x01\x00\x00P\x01\x00\x00\x00\x00\x00\x00\xbd\x00\x00\x00\x00\x00\x00\x00S\x01\x00\x00\x00\x00\x00\x00#\x01\x00\x00_\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\r\n\x01\x00\x00\xfa\x00\x00\x00\x00\x00\x00\x00,\x01\x00\x00@\x01\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00`\x00\x00\x00V\x01\x00\x00\xf5\x00\x00\x00\x00\x00\x00\x00%\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x01\x00\x00A\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\xb7\x00\x00\x00\xa2\x00\x00\x00M\x01\x00\x00]\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\\x01\x00\x00\x00\x00\x00\x00/\x01\x00\x00\xdc\x00\x00\x00&\x01\x00\x00C\x00\x00\x00\xc8\x00\x00\x00m\x00\x00\x00$\x01\x00\x00\xe0\x00\x00\x005\x01\x00\x00\xf0\x00\x00\x00\xcd\x00\x00\x00~\x00\x00\x00\x00\x00\x00\x00H\x01\x00\x00\xe5\x00\x00\x00\x87\x00\x00\x00\x10\x00\x00\x00;\x01\x00\x00r\x00\x00\x00\xfc\x00\x00\x00i\x00\x00\x00\x10\x01\x00\x003\x01\x00\x00\xec\x00\x00\x00\xb5\x00\x00\x00\x0c\x01\x00\x00\x0f\x00\x00\x00\x15\x01\x00\x00l\x00\x00\x00U\x01\x00\x00\xa1\x00\x00\x00\"\x00\x00\x00\x00\x00\x00\x00\x1e\x01\x00\x00\x00\x00\x00\x00D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00W\x01\x00\x00\x1b\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002\x00\x00\x00\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00M\x00\x00\x00\x00\x00\x00\x00F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x001\x00\x00\x00K\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Y\x00\x00\x00W\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00v\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\x00\x00\x00\x0c\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00a\x00\x00\x00\x00\x00\x00\x00&\x00\x00\x00\x00\x00\x00\x00R\x00\x00\x00\x00\x00']
        else:
            blist = [b':']
        if buf.endswith(b'/bin/busybox ECCHI\r\n'):
            blist.append(b'ECCHI: applet not found\r\n>')
        self.on_response(blist)
