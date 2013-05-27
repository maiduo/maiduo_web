#! -*- encoding:utf-8 -*-
from pdb import set_trace as bp
from os import getcwd
from os.path import isfile, expanduser, join
import ConfigParser


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def copy_file(src, dest):
    while True:
        _buffer = src.read(1024 * 4)
        if not _buffer:
            dest.flush()
            return
        dest.write(_buffer)

class NotFound(Exception):
    pass

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

def scan_default_location(filename):
    home = expanduser("~")
    for directory in [getcwd(), home, '/etc/']:
        full_config_path = join(directory, filename)
        if isfile(full_config_path):
            return full_config_path

    raise NotFound()

class MDConfig(ConfigParser.SafeConfigParser, Singleton):
    def __init__(self, config_path = None):
        if not config_path:
            config_path = scan_default_location("md.cfg")

        ConfigParser.SafeConfigParser.__init__(self)
        self.read(config_path)


