#! -*- encoding:utf-8 -*-
from pdb import set_trace as bp
from os import getcwd
from os.path import isfile, expanduser, join
from StringIO import StringIO
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

DEFAULT_MD_CONFIG = StringIO("""[storage]
access_key =
secret_key =
bucket = maiduo-dev

[common]
database = sqlite
enviroment = dev

[django_setting]
media_root =


[mysql]
host =
port = 3306
user = root
pass = 
name = himaiduo

[sqlite]
name = dev.sqlite
""")

class MDConfig(ConfigParser.SafeConfigParser, Singleton):
    def __init__(self, config_fp = None):
        if hasattr(self, 'initialized'):
            return

        if not config_fp:
            try:
                config_fp = file(scan_default_location("md.cfg"))
            except NotFound:
                # FIXME logging.info中输出 NotFound的描述
                pass

        ConfigParser.SafeConfigParser.__init__(self)
        self.readfp(config_fp)
        self.load_default()

        self.initialized = True

    def load_default(self):
        cfg = ConfigParser.SafeConfigParser()
        cfg.readfp(DEFAULT_MD_CONFIG)

        for section in cfg.sections():
            options = dict(cfg.items(section)).keys()
            
            if not self.has_section(section):
                self.add_section(section)

            for option in options:
                if not self.has_option(section, option):
                    self.set(section, option, cfg.get(section, option))
