import json
import hmac
import time
from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode

class Token(object):
    def __init__(self, access, secret):
        self.access = access
        self.secret = secret

    def encode(data):
        if isinstance(data, dict):
            data = json.dumps(data, separators=(',',':'))
        data = urlsafe_b64encode(data)
        signed = urlsafe_b64encode(hmac.new(self.secret, data, sha1).digest())

        return "%s:%s:%s" % (self.access, signed, data) 

    def check(self, data):
        pass

    def decode(data):
        pass

def pascal_to_camel_case(variable_name):
    variables = variable_name.split("_")
    _changed = [variables[0]]
    for i in range(1, len(variables)):
        variable = variables[i]
        _changed.append("%s%s" % (variable[0].upper(), variable[1:]))

    return "".join(_changed)

class PutToken(object):
    """copy from qiniu-sdk
    """

    JSON_FIELDS_MAP = ['scope', 'deadline', 'callback_url',\
                       'callback_body_type', 'customer', 'async_ops',\
                       'escape', 'detect_mine']

    def __init__(self, token, scope, expire = 3600, callback_url=None,\
                 callback_body_type=None, customer=None, async_ops=None,\
                 escape=None, detect_mine=None):
        self.scope = scope
        self.expire = int(time.time()) + expire
        self.callback_url = callback_url
        self.callback_body_type = callback_body_type
        self.customer = customer
        self.async_ops = async_ops
        self.escape = escape
        self.detect_mine = detect_mine
        self.token = token

    @property
    def dict(self):
        kv = dict()
        for field in self.JSON_FIELDS_MAP:
            if getattr(self, field, None):
                camel_case = pascal_to_camel_case(field)
                kv[camel_case] = getattr(self, field, None)

        return kv

    @property
    def json(self):
        return json.dumps(self.dict, separators=(',',':'))
