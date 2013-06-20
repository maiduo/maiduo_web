import re
import json
import hmac
import time
from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode
from pdb import set_trace as bp

class SignAuthenticateFault(Exception):
    pass

class Token(object):
    def __init__(self, access, secret):
        if isinstance(access, unicode):
            access = str(access)
        if isinstance(secret, unicode):
            secret = str(secret)
        self.access = access
        self.secret = secret

    def encode(self, data):
        if isinstance(data, dict):
            data = json.dumps(data, separators=(',',':'))
        data = urlsafe_b64encode(data)
        signed = urlsafe_b64encode(hmac.new(self.secret, data, sha1).digest())

        return "%s:%s:%s" % (self.access, signed, data) 

    def check(self, signature, content):
        return signature == urlsafe_b64encode(\
                               hmac.new(self.secret, content, sha1).digest())

    def put_token(self, encoded):
        return RequestToken.create(encoded)


def pascal_to_camel_case(variable_name):
    variables = variable_name.split("_")
    _changed = [variables[0]]
    for i in range(1, len(variables)):
        variable = variables[i]
        _changed.append("%s%s" % (variable[0].upper(), variable[1:]))

    return "".join(_changed)

def camel_case_to_pascal(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class Scope(object):
    def __init__(self, bucket, key=""):
        self.bucket = bucket
        self.key = key
        
    def __str__(self):
        if not self.key:
            return "%s" % self.bucket

        return "%s:%s" % (self.bucket, self.key)

    def __repr__(self):
        return str(self)

    @staticmethod
    def create(scope_string):
        if -1 == scope_string.find(":"):
            scope_string += ":"

        bucket, key = scope_string.split(":")

        return Scope(bucket, key)

class RequestPutToken(Token):
    """copy from qiniu-sdk
    """

    JSON_FIELDS_MAP = ['scope', 'deadline', 'callback_url',\
                       'callback_body_type', 'customer', 'async_ops',\
                       'escape', 'detect_mine']

    def __init__(self, access, secret, scope, expire = 3600, callback_url=None,\
                 callback_body_type=None, customer=None, async_ops=None,\
                 escape=None, detect_mine=None):
        self.scope = scope
        self.deadline = int(time.time()) + expire
        self.callback_url = callback_url
        self.callback_body_type = callback_body_type
        self.customer = customer
        self.async_ops = async_ops
        self.escape = escape
        self.detect_mine = detect_mine
        
        super(RequestPutToken, self).__init__(access, secret)

    @property
    def dict(self):
        kv = dict()
        for field in self.JSON_FIELDS_MAP:
            if getattr(self, field, None):
                camel_case = pascal_to_camel_case(field)
                kv[camel_case] = str(getattr(self, field, None))

        return kv

    @property
    def json(self):
        return json.dumps(self.dict, separators=(',',':'))

    @staticmethod
    def from_json(access, secret, request_token_json):
        if isinstance(request_token_json, dict):
            request_token = request_token_json
        else:
            if isinstance(request_token_json, unicode):
                request_token_json = str(request_token_json)
            request_token_json = urlsafe_b64decode(request_token_json)
            request_token = json.loads(request_token_json)

        for key in request_token.keys():
            v = request_token.pop(key)
            request_token[camel_case_to_pascal(key)] = v

        deadline = request_token.pop("deadline")
        scope = Scope.create(request_token.pop("scope", ""))

        return RequestPutToken(access, secret, scope, **request_token)

