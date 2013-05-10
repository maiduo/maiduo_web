#! -*- encoding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from ios_notifications.models import Device, APNService
from pdb import set_trace as bp

MESSAGE_TYPE_CHOICES = (\
    ("T", "Text",),
    ("V", "Video", ),
    ("I", "Image", )
)

# class ActivityManager(models.Manager):


class Activity(models.Model):
    owner = models.ForeignKey(User, default=0)
    user = models.ManyToManyField(User, related_name='participate')
    subject = models.CharField(max_length=255)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    def devices(self, service):
        apns = APNService.objects.get(name=service)
        # FIXME
        # 有严重的性能问题，现在的代码紧紧为了测试
        # 应该优化查询一次从数据库种查询到所有数据
        # 思路是在DeivceManager中提供一个返回apns的过滤
        # 有可能是错的，因为token和service的unique_together，并不代表service
        # 条件是唯一的

        return [user.ios_devices.filter(service=apns)[0] \
                for user in self.user.all()]

    def __unicode__(self):
        return self.subject

class Message(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    message_type = models.CharField(u"Type", choices=MESSAGE_TYPE_CHOICES, \
                                    default="Text", max_length=1)
    body = models.TextField()
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True, auto_now=True)

class MessageAddOns(models.Model):
    message = models.ForeignKey(Message)
    body = models.CharField(max_length=255)

class Chat(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    text = models.CharField(max_length=4000)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-create_at']

