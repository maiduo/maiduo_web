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

class ActivityManager(models.Manager):

    def create_with_invitations(self, invitations, *args, **kwargs):
        activity = self.create(*args, **kwargs)

        add_list = User.objects.filter(username__in=invitations)
        add_hash = dict([(i.username, i.username) for i in add_list])
        add_set  = set(add_hash.values())
        invitations = set(invitations) - add_set

        for user in add_list:
            activity.user.add(user)

        ActivityInvite.objects.create_with_invitations(activity, invitations)

        return activity


    def i_am_coming(self, user):
        invitations = ActivityInvite.objects.filter(user=user, avaiable=True)
        for invitation in invitations:
            invitation.activity.user.add(user)

        invitations.update(avaiable=False)


class Activity(models.Model):
    owner = models.ForeignKey(User, default=0)
    user = models.ManyToManyField(User, related_name='participate')
    subject = models.CharField(max_length=255)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    objects = ActivityManager()

    class Meta:
        ordering = ['-create_at']

    def save(self, *args, **kwargs):
        super(Activity, self).save(*args, **kwargs)
        

    def devices(self, service, exclude = None):
        apns = APNService.objects.get(name=service)
        # FIXME
        # 有严重的性能问题，现在的代码仅仅为了测试
        # 优化一次从数据库种查询到所有数据
        # 思路是在DeivceManager中提供一个返回apns的过滤
        # 有可能是错的，因为token和service的unique_together，并不代表service
        # 条件是唯一的

        user_query_set = exclude and self.user.exclude(\
                                        id__in=[user.id for user in exclude])\
                                 or self.user.all()

        _devices = []
        for user in user_query_set:
            user_devices = user.ios_devices.filter(service=apns)
            if 0 < len(user_devices):
                _devices.append(user_devices[0])
        return _devices

    @property
    def invitations(self):
        return ActivityInvite.objects.filter(activity=self)

    def __unicode__(self):
        return self.subject

class ActivityInviteManager(models.Manager):
    def create_with_invitations(self, activity, invitations):
        invitation_objects = []
        for invitation in invitations:
            invitation_objects.append(\
                self.create(activity=activity, username=invitation))

        return  invitation_objects

class ActivityInvite(models.Model):
    activity = models.ForeignKey(Activity)
    user = models.ForeignKey(User, related_name="users", default=0)
    refer = models.ForeignKey(User, related_name="refers", default=0)
    avaiable = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    objects = ActivityInviteManager() 

class Message(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    message_type = models.CharField(u"Type", choices=MESSAGE_TYPE_CHOICES, \
                                    default="Text", max_length=1)
    body = models.TextField()
    addons = models.IntegerField(default=0)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        ordering = ['-create_at']

class MessageAddon(models.Model):
    message = models.ForeignKey(Message)
    extra = models.CharField(max_length=255, default="", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.message.addons += 1
        self.message.save()

        super(MessageAddon, self).save(*args, **kwargs)

class Chat(models.Model):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    text = models.CharField(max_length=4000)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

class UserToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=6)
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)

class SMSLog(models.Model):
    content = models.CharField(max_length=255)
    mobile = models.TextField()
    ip = models.GenericIPAddressField('IPv4')
    create_at = models.DateTimeField(auto_now_add=True)
