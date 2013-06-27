#!/usr/bin/env python
#! -*- encoding:utf-8 -*-

from oauthost.decorators import oauth_required
from oauthost import auth_views
from piston.handler import BaseHandler
from piston.utils import rc, validate
from models import Message, MessageAddon, Activity, Chat, ActivityInvite
from forms import MessageForm
from django.db import IntegrityError
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import simplejson
from django.utils import timezone
from django.contrib.auth.models import User
from os.path import basename, dirname, join
from ios_notifications import models as push_models
from urllib import urlopen
from os.path import join
from pdb import set_trace as bp
import os
import utils
import hashlib
import PIL.Image
import random
import qiniu.config
import qiniu.auth_token

cfg = utils.MDConfig()
qiniu.config.ACCESS_KEY = cfg.get("storage", "access_key")
qiniu.config.SECRET_KEY = cfg.get("storage", "secret_key")

# 构建消息发送功能时，必须使用Mock的Notification相关对象，也就是说不能真的把消息
# 推送出去，所以没有直接引入APNService等对象，而是引入模块，以方便在测试用例中替
# 换

USER_FIELDS = ('user', ('id', 'first_name', 'date_joined', 'last_login'))

class SMS(object):
    def send(self, mobile, content):
        sms_url = "http://www.smsbao.com/sms?u=himaiduo&p=&m=%s&c=%s"
        fd = urlopen(sms_url % (mobile, content))
        responseText = fd.read(10)
        fd.close()

class SMSFactory(object):
    def create(self):
        return SMS()

class MDHandler(BaseHandler):
    def __init__(self, sms_factory = SMSFactory(), *args, **kwargs):
        self.sms = sms_factory.create()
        super(MDHandler, self).__init__(*args, **kwargs)

    def _storage_image_thumbnail(self, image, id, path, width):
        media_root = settings.MEDIA_ROOT
        preview_path = join("user", path, "%d/%d_%d.jpg" % ids + [width])
        preview_fd = file(os.path.join(media_root, preview_path), "w+")

        if w > width:
            preview_size = (width, h * (w / width))
        else:
            preview_size = (w, h)

        src.seek(0)

        preview_fd.seek(0)
        preview = PIL.Image.open(image)
        if w > width:
            preview.thumbnail(preview_size, PIL.Image.ANTIALIAS)
        preview.save(preview_fd.name, "JPEG")

        src.seek(0)
        preview_fd.close()

    def _storage_image(self, image, id, path, width):
        if not image:
            return
        ids = (id % 1000, id)
        origin_path = join("user", path, "%d/%d.jpg" % ids)
        media_root = settings.MEDIA_ROOT
        try:
            os.makedirs(dirname(join(media_root, origin_path)))
        except OSError:
            pass

        origin_fd = file(os.path.join(media_root, origin_path), "w+")

        utils.copy_file(src, origin_fd)
        origin_fd.seek(0)
        original = PIL.Image.open(origin_fd)
        w, h = original.size
        if not "JPEG" == original.format:
            original.save(origin_fd.name, "JPEG")
        origin_fd.close()

        for i in width:
            self._storage_image_thumbnail(image, id, path, i)
        src.close()
        origin_fd.close()


    def _send_sms(self, mobile, content):
        self.sms.send(mobile, content)

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
    allowed_method = ('GET', 'POST', 'PUT',)
    exclude = ('ip',)
    fields = ('id', 'body', 'message_type', 'create_at', 'stash', USER_FIELDS,\
              'activity')

    def read(request):
        pass

    def update(self, request):
        stash = bool(request.PUT.get("stash", False))
        message_id = request.PUT.get("message_id", 0)
        service = request.PUT.get("service", "dev")
        msg = Message.objects.get(pk=message_id)
        if not msg.stash == stash:
            msg.stash = stash
            msg.save()

        if not stash:
            activity = msg.activity
            push_text = u"%s:%s" % (request.user.first_name, msg.body)
            notification = push_models.Notification(message=push_text)
            notification.extra = {\
                "activity_id": activity.id,
                "message_id": msg.id,
                "user_id": request.user.id,
                "message_body": push_text,
                "message_type": msg.message_type,
                "type": "message",
            }
            devices = activity.devices(service, exclude=[request.user])
            send_notification(devices, service, notification)
        return msg

    def create(self, request):
        attrs = self.flatten_dict(request.POST)
        ip_address = utils.get_client_ip(request)
        message_body = attrs.get("body", None)
        activity_id = attrs.get("activity_id", 0)
        service = attrs.get("service", "dev")
        stash = bool(attrs.get("stash", False))
        try:
            activity = Activity.objects.get(pk=activity_id)
        except Activity.DoesNotExist:
            return rc.NOT_FOUND
        msg = Message(user=request.user, activity=activity, body=attrs['body'],\
                      ip=ip_address, message_type="T", stash=stash)

        msg.save()

        #Message.objects.filter(id=msg.id).update(stash=stash)
        """
        msg_id = msg.id
        msg = None
        msg = Message.objects.get(pk=msg_id)
        msg.stash = stash
        msg.save()
        try:
            msg.stash = 0
            msg.save()
        except Exception, e:
            print e
            bp()
        #self._storage_message_image(request, msg)
        """
        if not stash:
            push_text = u"%s:%s" % (request.user.first_name, message_body)
            notification = push_models.Notification(message=push_text)
            notification.extra = {\
                "activity_id": activity_id,
                "message_id": msg.id,
                "user_id": request.user.id,
                "message_body": push_text,
                "message_type": msg.message_type,
                "type": "message",
            }
            devices = activity.devices(service, exclude=[request.user])
            send_notification(devices, service, notification)
        return msg

class MessageAddonHandler(BaseHandler):
    allowed_method = ("POST", "GET",)
    fields = ("id", "message", "stash", "key", "width", "height", "size",\
              "create_at", "extra",)
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
        name = request.POST.get("name", "default.jpg")
        extra = request.POST.get("extra", "{}")
        width = request.POST.get("width", 0)
        height = request.POST.get("height", 0)
        size = request.POST.get("size", 0)

        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return rc.NOT_FOUND

        key = hashlib.sha256(str(random.random())).hexdigest()
        key = "%s.%s" % (key, name.split(".")[-1])

        cfg = utils.MDConfig()
        bucket = cfg.get("storage", "bucket")
        policy = qiniu.auth_token.PutPolicy("%s:%s" %(bucket, key))
        policy.expires = 3600 * 24
        upload_token = policy.token()

        msg = {\
            "message": message,
            "stash": False,
            "key": key,
            "width": width,
            "height": height,
            "size": size,
            "extra": extra
        }

        addon = MessageAddon.objects.create(**msg)

        return {\
            "addon": addon,
            "upload_token": upload_token,
        }


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
            'user_id': request.user.id,
            'chat_text': text,
            'type': 'chat',
        }
        devices = activity.devices(service, exclude=[request.user])
        send_notification(devices, service, notification)
        return chat

class ChatsHandler(BaseHandler):
    model = Chat
    allowed_method = ('GET',)
    exclude = ('ip')

    def read(self, request, activity_id):
        try:
            page = int(request.GET.get("page", 1))
        except ValueError:
            page = 1
        page_size = request.GET.get("page_size", settings.PER_PAGE_SIZE);
        try:
            page_size = int(page_size)
        except ValueError:
            page_size = settings.PER_PAGE_SIZE

        if page_size < 1 or page_size > 100:
            page_size = settings.PER_PAGE_SIZE

        kw_query = {\
            "activity_id": activity_id,
        }
        query_set = Chat.objects.filter(**kw_query)
        paginator = Paginator(query_set, page_size)

        if page > paginator.num_pages:
            return []
        chats = paginator.page(page).object_list
        chats = [i for i in chats]
        chats.reverse()

        return chats


class AuthenticationHandler(BaseHandler):
    allowed_method =('POST',)
    model = User
    fields = ('id', 'username', 'first_name')

    def bind_user_and_device_token(self, user, device_token, service_name):
        query = {\
            "users__id": user.id,
            "token": device_token,
            "service__name": service_name
        }
        not_bind = push_models.Device.objects.filter(**query).count() == 0
        empty_token = len(device_token) == 0

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



class LogoutHandler(BaseHandler):
    allowed_method = ('POST',)
    fields = ('id', 'username', 'first_name')
    exclude = ('password', 'ip')
    model = User

    def create(self, request):
        device_token = request.POST.get("device_token")

        request.user.ios_devices.filter(token=device_token).delete()
        devices = request.user.ios_devices.all()
        return rc.DELETED


class ActivityHandler(BaseHandler):
    model = Activity
    allowed_method = ('POST', 'READ', 'DELETE')

    fields = ('id', 'subject',\
              ('owner',('id', 'username', 'first_name')),\
              ('user',('id', 'username', 'first_name'),))
    exclude = ('ip', ('owner', ('password',)))

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
                    .create(**kw_activity)

        activity.user.add(request.user)
        return activity

    def delete(self, request):
        activity_id = request.GET.get("activity_id", 0)
        activity = Activity.objects.get(pk=activity_id)
        activity.delete()
        return rc.DELETED

class ActivityInviteHandler(BaseHandler):
    model = ActivityInvite
    allowed_method = ('POST',)

    def create(self, request):
        username = request.POST.get('username', None)
        name = request.POST.get('name', None)
        activity_id = request.POST.get('activity_id', 0)
        
        if activity_id < 1:
            return rc.NOT_FOUND
        
        now = timezone.now()
        try:
            invitation_user = User.objects.get(username=username)
        except User.DoesNotExist:
            invitation_user = User(username=username,first_name=name,
                                   is_active=False, is_staff=False, 
                                   is_superuser=False,last_login=now, 
                                   date_joined=now)

            invitation_user.set_password("%f" % random.random())
            # invitation_user.save()

        """invitation_user = ActivityInvite(refer=request.user,\
                                         user=invitation_user, 
                                         activity_id=activity_id)
        """
        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return rc.NOT_FOUND
        has_joined = activity.user.filter(id=invitation_user.id).count() > 0
        invitation_user.save()
        activity.save()
        if not has_joined:
            activity.user.add(invitation_user)
        return invitation_user

class UserHandler(MDHandler):
    model = User
    allowed_method = ('POST', 'PUT',)
    fields = ('id', 'username', 'first_name', 'date_joined', 'last_login',)
    exclude = ('password', 'is_superuser', 'is_staff', 'email', 'is_active',
               'last_login', 'date_joined', 'last_name', )
    
    def update(self, request):
        if request.FILES.get("avatar", None):
            self._storage_image(request.FILES['avatar'], request.user.id,\
                                'avatar', [100, 200, 400])
        return rc.ALL_OK

    def create(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        name = request.POST.get("name", None)
        try:
            user = User.objects.create_user(username=username,\
                                            password=password)
        except IntegrityError:
            user = User.objects.get(username=username)
            if user.is_active:
                return rc.BAD_REQUEST

            # Activity.objects.i_am_coming(user)
        user.is_active = True
        user.first_name = name
        user.set_password(password)
        user.save()

        return user

    def read(self, request, username):
        return User.objects.get(username=username)

class ProfileHandler(MDHandler):
    model = User
    allowed_method = ('PUT',)

    def update(self, request):
        cfg = utils.MDConfig()
        bucket = cfg.get("storage", "bucket")
        uid = request.user.id
        key = "%d/%d.jpg" % (uid % 1000, uid)
        policy = qiniu.auth_token.PutPolicy("%s:%s" %(bucket, key))
        policy.expires = 3600 * 24
        upload_token = policy.token()
        return {\
            "upload_token": upload_token,
        }
