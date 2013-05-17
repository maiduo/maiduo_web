#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from oauthost.decorators import oauth_required
from oauthost import auth_views
from piston.handler import BaseHandler
from piston.utils import rc, validate
from models import Message, MessageAddon, Activity, Chat
from forms import MessageForm
from django.db import IntegrityError
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import simplejson
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

class MessagesHandler(BaseHandler):
    model = Message
    allowed_method = ('GET',)
    exclude = ('ip',)

    def read(self, request, activity_id):
        page = request.GET.get("page", 1)
        
        kwquery = {\
            "activity_id": activity_id,
            "user_id": request.user.id
        }
        try:
            query_set = Message.objects.filter(**kwquery)
            paginator = Paginator(query_set, settings.PER_PAGE_SIZE)
            return paginator.page(page).object_list
        except Message.DoesNotExist:
            return rc.NOT_FOUND

class MessageHandler(BaseHandler):
    model = Message
    allowed_method = ('GET', 'POST',)
    exclude = ('ip',)

    def read(request):
        pass

    #@oauth_required(scope_auto=True)
    #@validate(MessageForm)

    def create(self, request):
        attrs = self.flatten_dict(request.POST)
        ip_address = utils.get_client_ip(request)
        message_body = attrs.get("body", None)
        activity_id = attrs.get("activity_id", 0)
        service = attrs.get("service", "dev")
        try:
            activity = Activity.objects.get(pk=activity_id)
        except Activity.DoesNotExist:
            return rc.NOT_FOUND

        msg = Message(user=request.user, activity=activity, body=attrs['body'],\
                      ip=ip_address, message_type="T")
        msg.save()
        #self._storage_message_image(request, msg)
        push_text = u"%s:%s" % (request.user.first_name, message_body)
        notification = push_models.Notification(message=push_text)
        notification.extra = {\
            "activity_id": activity_id,
            "message_id": msg.id,
            "user": request.user.id,
            "type": "message",
        }
        devices = activity.devices(service, exclude=[request.user])
        send_notification(devices, service, notification)
        return msg

class MessageAddonHandler(BaseHandler):
    allowed_method = ("POST", "GET",)
    fields = ("id", "extra",)
    def _storage_message_image(self, src, message_addon):
        if not src:
            return
        ids = (message_addon.id % 1000, message_addon.id)
        origin_path = "user/img/%d/%d.jpg" % ids
        preview_path = "user/img/%d/%d_preview.jpg" % ids
        media_root = settings.MEDIA_ROOT
        try:
            os.makedirs(dirname(join(media_root, origin_path)))
        except OSError:
            pass

        origin_fd = file(os.path.join(media_root, origin_path), "w+")
        preview_fd = file(os.path.join(media_root, preview_path), "w+")

        utils.copy_file(src, origin_fd)
        origin_fd.seek(0)
        original = PIL.Image.open(origin_fd)
        w, h = original.size
        if not "JPEG" == original.format:
            original.save(origin_fd.name, "JPEG")
        origin_fd.close()

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
        origin_fd.close()


        # Extra
        
        message_addon.extra = simplejson.dumps({\
            "preview_width": preview_size[0],
            "preview_height": preview_size[1],
            "preview_path": preview_path,
            "origin_width": w,
            "origin_height": h,
            "origin_path": origin_path
        })
        message_addon.save()

    def create(self, request):
        message_id = request.POST.get("message_id", 0)
        extra = request.POST.get("extra", "{}")
        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return rc.NOT_FOUND


        addon = MessageAddon(message=message, extra=extra)
        addon.save()

        self._storage_message_image(request.FILES['attachment'], addon)

        return addon


def send_notification(devices, service, notification):
    cls_device = push_models.Device
    cls_apn_service = push_models.APNService
    
    apns = cls_apn_service.objects.get(name=service)
    notification.service = apns
    apns.push_notification_to_devices(notification, devices)

def send_notification_with_tokens(tokens, service, notification):
    cls_device = push_models.Device
    devices = cls_device.objects.filter(token__in=tokens, service=apns)
    send_notification(devices, service, notification)

class ChatHandler(BaseHandler):
    model = Chat
    allowed_method = ('GET', 'POST',)
    fields = ("id", ("user", ("id", "first_name",)), "text",\
              ("activity", ("id",)), "create_at" )
    exclude = ('ip',)

    def read(self, request, chat_id):
        try:
            return Chat.objects.get(pk=chat_id)
        except Chat.DoesNotExist:
            return rc.NOT_FOUND

    def create(self, request):
        activity_id = request.POST.get("activity_id", 0)
        text = request.POST.get("text", "")
        service = request.POST.get("service", "dev")
        try:
            #TODO 检查用户是否有权限发布消息
            activity = Activity.objects.get(pk=activity_id)
        except Activity.DoesNotExist:
            activity = None
        if not activity:
            return rc.NOT_FOUND
        
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
            'chat_id': chat.id,
            'user_id': request.id,
            'type': 'chat',
        }
        send_notification(activity.devices(service, exclude=[request.user]), \
                          service, notification)
        return chat

class ChatsHandler(BaseHandler):
    model = Chat
    allowed_method = ('GET',)
    exclude = ('ip')

    def read(self, request, activity_id):
        page = request.GET.get("page", 1)
        kw_query = {\
            "activity_id": activity_id,
            "user_id": request.user.id
        }
        query_set = Chat.objects.filter(**kw_query)
        paginator = Paginator(query_set, settings.PER_PAGE_SIZE)

        return paginator.page(page).object_list


class AuthenticationHandler(BaseHandler):
    allowed_method =('POST',)

    def bind_user_and_device_token(self, user, device_token, service_name):
        query = {\
            "users__id": user.id,
            "token": device_token,
            "service__name": service_name
        }
        not_bind = push_models.Device.objects.filter(**query).count() == 0
        empty_token = '' == device_token
        if not_bind and not empty_token:
            service = push_models.APNService.objects.get(name=service_name)
            kw_device = {\
                "token": device_token,
                "service": service,
            }
            try:
                device = push_models.Device.objects.get(**kw_device)
            except push_models.Device.DoesNotExist:
                device = push_models.Device.objects.create(**kw_device)
            user.ios_devices.add(device)


    def create(self, request):
        rsp = auth_views.endpoint_token(request)
        JSON = simplejson.loads(rsp.content)

        auth_success = JSON.get("access_token", None) and True or False
        if auth_success:
            user = User.objects.get(username=request.POST.get("username"))
            self.bind_user_and_device_token(user,\
                                            request.POST.get("device_token",
                                                             ""),\
                                            request.POST.get("service", "dev"))

        JSON['user'] = user
        return JSON


class ActivityHandler(BaseHandler):
    model = Activity
    allowed_method = ('POST', 'READ')
    fields = ('id', 'subject', 'owner', 'user',)
    exclude = ('ip', 'create_at', 'update_at')

    def read(self, request):
        return Activity.objects.filter(user=request.user)

    def create(self, request):
        subject = request.POST.get("subject", "")
        invitations = request.POST.get("invitation", "").split(",")
        ip_address = utils.get_client_ip(request)
        kw_activity = {
            "subject": subject,
            "owner": request.user,
            "ip": ip_address
        }
        activity = Activity\
                    .objects\
                    .create_with_invitations\
                        (invitations, **kw_activity)
        activity.user.add(request.user)
        return activity

class UserHandler(BaseHandler):
    model = User
    allowed_method = ('POST',)
    exclude = ('password', 'is_superuser', 'is_staff', 'email', 'is_active',
               'last_login', 'date_joined', 'last_name', )

    def create(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        try:
            user = User.objects.create_user(username=username,\
                                            password=password)
            Activity.objects.i_am_coming(user)
        except IntegrityError:
            bad = rc.BAD_REQUEST
            bad.write("User has exists.")
            return bad
        return user

    def read(self, request, username):
        return User.objects.get(username=username)
