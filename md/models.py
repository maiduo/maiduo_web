#! -*- encoding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

MESSAGE_TYPE_CHOICES = (\
    ("T", "Text",),
    ("V", "Video", ),
    ("I", "Image", )
)

class Message(models.Model):
    user = models.ForeignKey(User)
    message_type = models.CharField(u"Type", choices=MESSAGE_TYPE_CHOICES, \
                                    default="Text", max_length=1)
    body = models.TextField()
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True, auto_now=True)

class MessageAddOns(models.Model):
    message = models.ForeignKey(Message)
    body = models.CharField(max_length=255)
