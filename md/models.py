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
    message_type = models.CharField(u"Type", choices=MESSAGE_TYPE_CHOICES)
    body = message.TextField()
    ip = models.CharField(u"IP Address", max_length=15)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField()
