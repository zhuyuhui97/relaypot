import yaml
from yaml import CLoader as Loader

from relaypot import utils
from relaypot.utils.mods import get_agent_class, get_writer_class
from relaypot.utils.vars import load_git_rev


def init_common(conf_path):
    load_config_file(conf_path)
    load_git_rev()
    utils.cls_writer = get_writer_class()

def init_agent():
    utils.cls_agent = get_agent_class()


def load_config_file(conf_path):
    with open(conf_path) as conffile:
        utils.global_config = yaml.load(conffile, Loader=Loader)
