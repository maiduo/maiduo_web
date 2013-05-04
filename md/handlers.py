#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from models import Message
from oauthost.decorators import oauth_required
from piston.handler import BaseHandler
from piston.utils import rc, validate
from models import Message, MessageAddOns, Activity
from forms import MessageForm
from django.conf import settings
from os.path import basename, dirname, join
import os
import utils
import PIL.Image
from pdb import set_trace as bp

class MessageHandler(BaseHandler):
    model = Message
    allowed_method = ('GET', 'POST',)
    exclude = ('id', 'ip', 'create_at', 'update_at',)

    def read(request):
        pass

    #@oauth_required(scope_auto=True)
    #@validate(MessageForm)
    def _storage_message_image(self, request, message):
        src = request.FILES.get('addons', None)
        if not src:
            return

        ids = (message.id % 1000, message.id)
        new_path = "user/img/%d/%d.jpg" % ids
        preview_path = "user/img/%d/%d_preview.jpg" % ids
        media_root = settings.MEDIA_ROOT
        try:
            os.makedirs(dirname(join(media_root, new_path)))
        except OSError:
            pass
        new_fd = file(os.path.join(media_root, new_path), "w+")
        preview_fd = file(os.path.join(media_root, preview_path), "w+")

        utils.copy_file(src, new_fd)
        new_fd.seek(0)
        original = PIL.Image.open(new_fd)
        w, h = original.size
        if not "JPEG" == original.format:
            original.save(new_fd.name, "JPEG")
        new_fd.close()

        if w > 620:
            preview_size = (620, h * (w / 620.0))
        else:
            preview_size = (w, h)

        src.seek(0)
        # utils.copy_file(src, preview_fd)
        preview_fd.seek(0)
        preview = PIL.Image.open(src)
        if w > 620:
            preview.thumbnail(preview_size, PIL.Image.ANTIALIAS)
        preview.save(preview_fd.name, "JPEG")

        src.close()
        preview_fd.close()
        new_fd.close()

        # MessageAddOns.objects.create(message=message, body=
        

    def create(self, request, **kwargs):
        # pdb.set_trace()
        attrs = self.flatten_dict(request.POST)
        ip_address = utils.get_client_ip(request)
        message_body = attrs.get("body", None)
        activity_subject = attrs.get("activity_subject", None)
        activity_id = attrs.get("acitivity_id", None)
        activity = None
        if not activity_id and ("" == activity_subject or not activity_subject):
            activity_subject = message_body[:20]
        if activity_subject:
            activity = Activity(user=request.user, subject=activity_subject,\
                                ip=ip_address)
            activity.save()
        if (not activity) and activity_id:
            activity_id = attrs.get("activity_id", None)
            if not activity_id:
                return rc.NOT_FOUND
            activity = Activity.objects.get(pk=activity_id)
        msg = Message(user=request.user, activity=activity, body=attrs['body'],\
                      ip=ip_address)
        msg.save()
        self._storage_message_image(request, msg)
        return rc.CREATED
