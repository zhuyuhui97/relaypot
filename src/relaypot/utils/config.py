import yaml
import os
from subprocess import run, PIPE

from relaypot import utils


def load_option(path):
    with open(path) as conffile:
        utils.global_config = yaml.load(conffile)

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