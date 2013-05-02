#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from models import Message
from piston.handler import BaseHandler
from piston.utils   import rc

class MessageHandler(BaseHandler):
    model = Message
    allowed_method = ('GET', 'POST',)
    exclude = ('id', 'ip', 'create_at', 'update_at',)

    def read(request):
        pass

    def create(request):
        form = MessageForm(request.POST)
        if form.is_valid():
            return rc.CREATED
        else:
            return rc.BAD_REQUESTED
