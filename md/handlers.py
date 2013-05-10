#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from oauthost.decorators import oauth_required
from piston.handler import BaseHandler
from piston.utils import rc, validate
from models import Message, MessageAddOns, Activity, Chat
from forms import MessageForm
from django.conf import settings
from django.contrib.auth.models import User
from os.path import basename, dirname, join
from ios_notifications import models as push_models
import os
import utils
import PIL.Image
from pdb import set_trace as bp

# 构建消息发送功能时，必须使用Mock的Notification相关对象，也就是说不能真的把消息
# 推送出去，所以没有直接引入APNService等对象，而是引入模块，以方便在测试用例中替
# 换

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

        preview_fd.seek(0)
        preview = PIL.Image.open(src)
        if w > 620:
            preview.thumbnail(preview_size, PIL.Image.ANTIALIAS)
        preview.save(preview_fd.name, "JPEG")

        src.close()
        preview_fd.close()
        new_fd.close()
        

    def create(self, request):
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


def send_notification(devices, service, notification):
    cls_device = push_models.Device
    cls_apn_service = push_models.APNService
    
    apns = cls_apn_service.objects.get(name=service)
    notification.service = apns
    apns.push_notification_to_devices(notification, devices, chunk_size=200)

def send_notification_with_tokens(tokens, service, notification):
    cls_device = push_models.Device
    devices = cls_device.objects.filter(token__in=tokens, service=apns)
    send_notification(devices, service, notification)

class ChatHandler(BaseHandler):
    model = Chat
    allowed_method = ('GET', 'POST',)
    exclude = ('id', 'ip', 'create_at', 'update_at',)

    def create(self, request):
        activity_id = request.POST.get("activity_id", 0)
        try:
            activity = Activity.objects.get(pk=activity_id)
        except Acitivity.DoesNotExists:
            activity = None
        text = request.POST.get("text", "")
        if not activity:
            not_found = rc.NOT_FOUND
            not_found.write("Activity id not found.")
            return not_foud
        
        if "" == text:
            empty = rc.BAD_REQUEST
            empty.write("Text can not empty.")
            return empty
        ip_address = utils.get_client_ip(request)
        chat = Chat(user=request.user, activity=activity, text=text, \
                    ip=ip_address)
        chat.save()

        notification = push_models.Notification(message=text)
        notification.extra = {\
            'activity_id': activity_id,
            'chat_id': chat.id
        }
        send_notification(activity.devices("dev", exclude=[request.user]), \
                          "dev", notification)
        return rc.CREATED

class ChatsHandler(BaseHandler):
    model = Chat
    allowed_method = ('GET',)
    exclude = ('ip')

    def read(request):
        pass


class UserHandler(BaseHandler):
    model = User
    allowed_method = ('POST',)
    exclude = ('password', 'is_superuser', 'is_staff', 'email',)

    def create(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = User.objects.create_user(username=username, password=password)
        return rc.CREATED

    def read(self, request, user_id):
        return User.objects.get(pk=1)
