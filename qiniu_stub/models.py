from django.db import models
from pdb import set_trace as bp
from base64 import urlsafe_b64decode
import token

class ServerPutToken(object):
    def __init__(self, request_data):
        self.access, self.signature, request_put_token = \
            request_data.split(":")

        try:
            credentail = Credential.objects.get(access=self.access)
        except Credential.DoesNotExist:
            raise token.SignAuthenticateFault()

        self.put_token= token.RequestPutToken.from_json(credentail.access,\
                                                        credentail.secret,\
                                                        request_put_token)

        if not self.put_token.check(self.signature, request_put_token):
            raise token.SignAuthenticateFault()
        

class Credential(models.Model):
    access = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)


class Key(models.Model):
    name = models.CharField(max_length=255)
    size = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

