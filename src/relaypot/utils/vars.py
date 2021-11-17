import random
import os

from relaypot import utils
from subprocess import run, PIPE

def get_home_path():
    filepath = os.path.abspath(__file__)
    root_path = os.path.join(filepath, '../../')
    root_path = os.path.normpath(root_path)
    return os.path.join(root_path)

def load_git_rev():
    cwd = get_home_path()
    res = run(['git','rev-parse','--short','HEAD'], stdout=PIPE, cwd=cwd)
    res.check_returncode()
    if res.returncode != 0:
        return 
    utils.git_rev = res.stdout.decode().strip()
    return utils.git_rev

def gen_sessid():
    # return base64.b64encode(os.urandom(32))[:8].decode()
    seed = '0123456789abcdef'
    return ''.join(random.choice(seed) for i in range(16))