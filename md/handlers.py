#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from models import Message
from oauthost.decorators import oauth_required
from piston.handler import BaseHandler
from piston.utils import rc, validate
from models import Message
from forms import MessageForm
from utils import get_client_ip
from pdb import set_trace as bp

class MessageHandler(BaseHandler):
    model = Message
    allowed_method = ('GET', 'POST',)
    exclude = ('id', 'ip', 'create_at', 'update_at',)

    def read(request):
        pass

    #@oauth_required(scope_auto=True)
    #@validate(MessageForm)
    def create(self, request, **kwargs):
        # pdb.set_trace()
        attrs = self.flatten_dict(request.POST)
        Message.objects.create(user=request.user, body=attrs['body'], \
                               ip=get_client_ip(request))
        return rc.CREATED
