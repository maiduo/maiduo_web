#! -*- encoding:utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import simplejson
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from django.contrib.auth.models import User
from django.conf import settings
from pdb import Pdb, set_trace as bp
from ios_notifications.models import Device, APNService
from models import Message, Activity, ActivityInvite, Chat
import handlers
import os
import utils
import mock

class OAuthTestCase(TestCase):
    fixtures = ['users', 'activity.json', 'ios_notifications.json',\
                'oauthost.json']
                
    @override_settings(DEBUG=True)
    def setUp(self):
        self.client = Client()
        request_token = {\
            'client_id': '2dc5d858f1f441aa8e957b82ce248816',
            'username': 'test',
            'password': '123123',
            'grant_type': 'password',
            'scope': '',
        }
        rsp = self.client.post('/api/token/', request_token)
        self.assertEquals(200, rsp.status_code)

        json = simplejson.loads(rsp.content)
        self.access_token = json['access_token']
        self.refresh_token = json['refresh_token']

class ActivityManagerTest(TestCase):
    fixtures = ['users', 'activity.json',]

    def _test_create_with_invitations(self):
        owner = User.objects.get(pk=1)
        activity = Activity.objects.create_with_invitations(
            ['13000000000', 'test',], subject='Activity subject', owner=owner,\
            ip='127.0.0.1')

        user1 = activity.user.get(username="test")
        self.assertNotEquals(None, user1)
        self.assertEquals("13000000000", activity.invitations[0].username)

    def test_i_am_coming(self):
        user = User.objects.get(username="13000000001")
        Activity.objects.i_am_coming(user)
        invitations = ActivityInvite.objects.filter(user=user)
        self.assertNotEquals(0, Activity.objects.filter(user=user).count())
        self.assertNotEquals(0, invitations.count())
        for invitation in invitations:
            self.assertEquals(False, invitation.avaiable)

class ActivityModelTest(TestCase):
    fixtures = ['users', 'activity.json', 'ios_notifications.json']

    def test_devices(self):
        service = APNService.objects.get(name="dev")
        user1 = User.objects.get(pk=1)
        devices = Activity.objects.get(pk=1).devices(service, exclude=[user1])
        self.assertEquals(2, len(devices))
        self.assertEquals("dev", devices[0].service.name)

class ActivityHandlerTest(OAuthTestCase):
    def test_read(self):
        activity_url = '/api/activity/?access_token=%s' % self.access_token
        rsp = self.client.get(activity_url)
        activities = simplejson.loads(rsp.content)
        self.assertEquals(200, rsp.status_code)
        self.assertEquals(2, len(activities))
        self.assertEquals(1, activities[0]['owner']['id'])

    def test_delete(self):
        request = {\
            "access_token": self.access_token,
            "activity_id": 1,
        }

        rsp = self.client.delete('/api/activity/', request)
        print rsp.content

        self.assertEquals(204, rsp.status_code)

        self.assertEquals(0, len(Activity.objects.filter(pk=1)))


    def test_create(self):
        activity_subject_name = "The second activity."
        request_data = {
            "subject": activity_subject_name,
            "access_token": self.access_token,
            "invitations": "13000000001,",
        }
        rsp = self.client.post('/api/activity/', request_data)
        self.assertEquals(200, rsp.status_code)

        activity = Activity.objects.get(subject=activity_subject_name)
        self.assertEquals(activity_subject_name, activity.subject)

class ActivityInviteHandlerTest(OAuthTestCase):
    def test_create_has_user(self):
        request_data = {
            "activity_id": 1,
            "username": "13000000001",
            "name": "13000000001",
            "access_token": self.access_token
        }

        rsp = self.client.post('/api/activity/invite/', request_data)
        self.assertEquals(200, rsp.status_code)

        rsp = self.client.post('/api/activity/invite/', request_data)
        self.assertEquals(200, rsp.status_code)

        user = User.objects.get(username="13000000001")
        user_test = User.objects.get(username="test")
        activity = Activity.objects.get(pk=1)

        self.assertEquals(1, activity.user.filter(id=user.id).count())


class UserHandlerTest(TestCase):

    fixtures = ['users', 'activity.json']
    
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        user_data = {\
            "username": "13000000001",
            "password": "13000000000",
            "name": u"袁德俊",
        }
        rsp = self.client.post('/api/user/', user_data)
        self.assertEquals(200, rsp.status_code)

        user = User.objects.get(username="13000000001")
        self.assertNotEquals(None, user)

        activity = Activity.objects.get(pk=1)
        joined = activity.user.get(pk=user.id)
        self.assertNotEquals([], joined)
        self.assertEquals(True, user.is_active)

class MessageHandlerTest(OAuthTestCase):
    fixtures = ['users', 'oauthost.json', 'activity.json', \
                'ios_notifications.json']

    def test_create_text_message(self):
        ios_notifications_models = handlers.push_models
        utils_module = handlers.utils

        handlers.push_models = mock.MagicMock()
        handlers.utils = mock.MagicMock()
        handlers.utils.get_client_ip.return_value = "127.0.0.1"
        hd = handlers.MessageHandler()
        request = mock.MagicMock()
        request.user = User.objects.get(username='test')
        request.POST = {"activity_id": 1, "body": "Message."}

        def mock_and_assert_send_notification(devices, service, notification):
            self.assertEquals(2, len(devices))

        original_send_notification = handlers.send_notification
        handlers.send_notification = mock_and_assert_send_notification
        hd.create(request)
        handlers.send_notification = original_send_notification

        msg = Message.objects.get(body="Message.")
        self.assertNotEquals(None, msg)

        activity = Activity.objects.get(pk=1)

        handlers.push_models = ios_notifications_models
        handlers.utils = utils_module

class MessagesHandlerTest(OAuthTestCase):
    def test_read(self):
        rsp = self.client.get("/api/messages/1/?access_token=%s"\
                              % self.access_token)
        self.assertEquals(200, rsp.status_code)

class MessageAddonHandlerTest(OAuthTestCase):
    fixtures = ['users', 'oauthost.json', 'activity.json', \
                'ios_notifications.json']

    def test_create(self):
        attachment = file("resources/10x10.png", "r")
        addons_data = {\
            "message_id": 1,
            "access_token": self.access_token,
            "attachment": attachment
        }
        rsp = self.client.post("/api/message/addon/", addons_data)
        self.assertEquals(201, rsp.status_code)


class HandlerTest(TestCase):
    def test_send_notification_with_token(self):
        ios_notifications_models = handlers.push_models

        handlers.push_models = mock.MagicMock()
        handlers.send_notification([], "dev", mock.MagicMock())

        handlers.push_models = ios_notifications_models

class AuthenticationHandlerTest(TestCase):
    fixtures = ['users', 'activity.json', 'ios_notifications.json',\
                'oauthost.json']

    def setUp(self):
        self.client = Client()

    def test_bind_user_and_device_token_not_exists_token(self):
        device_token = "<token>"
        auth = handlers.AuthenticationHandler()
        user = User.objects.get(username="test")
        auth.bind_user_and_device_token(user, device_token, "dev")

        devices = Device.objects.filter(users=user, token=device_token,\
                                        service__name="dev").count()
        self.assertEquals(1, devices)

    def test_bind_user_and_device_token(self):
        device_token = "a4faf00f4654246b9fd7e78ae29a49b321673892ae81721b8e74ad9d285b3c27"
        auth = handlers.AuthenticationHandler()
        user = User.objects.get(username="test")
        auth.bind_user_and_device_token(user, device_token, "dev")

        devices = Device.objects.filter(users=user, token=device_token,\
                                        service__name="dev").count()
        self.assertEquals(1, devices)
                                
    def test_bind_user_and_device_token_but_token_exist(self):
        device_token = "a4faf00f4654246b9fd7e78ae29a49b321673892ae81721b8e74ad9d285b3c30"
        auth = handlers.AuthenticationHandler()
        user = User.objects.get(username="test")
        auth.bind_user_and_device_token(user, device_token, "dev")

        devices = Device.objects.filter(users=user, token=device_token,\
                                        service__name="dev").count()
        self.assertEquals(1, devices)

    @override_settings(DEBUG=True)
    def test_authenticate(self):
        request_token = {\
            'client_id': '2dc5d858f1f441aa8e957b82ce248816',
            'username': 'test',
            'password': '123123',
            'grant_type': 'password',
            'scope': '',
            'device_token': 'a4faf00f4654246b9fd7e78ae29a49b321673892ae81721b8e74ad9d285b3c27',
        }
        rsp = self.client.post('/api/authentication/', request_token)

        self.assertEquals(200, rsp.status_code)
        user = User.objects.get(username="test")
        devices = Device.objects.filter(users=user, token="<token>",\
                                        service__name="dev").count()
        self.assertEquals(1, devices)

    @override_settings(DEBUG=True)
    def test_authenticate_empty_token(self):
        request_token = {\
            'client_id': '2dc5d858f1f441aa8e957b82ce248816',
            'username': 'test',
            'password': '123123',
            'grant_type': 'password',
            'scope': '',
            'device_token': '',
        }
        rsp = self.client.post('/api/authentication/', request_token)
        self.assertEquals(200, rsp.status_code)
        user = User.objects.get(username="test")
        devices = Device.objects.filter(users=user, token="",\
                                        service__name="dev").count()
        self.assertEquals(0, devices)

class LogoutHandlerTest(OAuthTestCase):
    def test_authenticate_delete(self):
        t = "a4faf00f4654246b9fd7e78ae29a49b321673892ae81721b8e74ad9d285b3c27"
        request = {\
            "access_token": self.access_token,
            "device_token": t
        }
        rsp = self.client.post("/api/logout/", request)
        user1 = User.objects.get(pk=1)

        for device in user1.ios_devices.all():
            if device.token == t:
                self.assertTrue(False)
        
        self.assertTrue(True)

class ChatsHandlerTest(OAuthTestCase):
    def test_read(self):
        rsp = self.client.get("/api/chats/1/?access_token=%s&page_size=2&page=1"\
                              % self.access_token)
        chats = simplejson.loads(rsp.content)
        self.assertEquals(200, rsp.status_code)

    def test_read_page_size_equal_zero(self):
        rsp = self.client.get("/api/chats/1/?access_token=%s&page_size=0" \
                              % self.access_token)
        self.assertEquals(200, rsp.status_code)

    def test_read_page_great_max_page(self):
        rsp = self.client.get("/api/chats/1/?access_token=%s&page=100" \
                              % self.access_token)
        self.assertEquals('[]', rsp.content)
        self.assertEquals(200, rsp.status_code)


class ChatHandlerTest(OAuthTestCase):

    def test_read(self):
        rsp = self.client.get(
                "/api/chat/1/?access_token=%s" % self.access_token)
        self.assertEquals(200, rsp.status_code)

    """
    def test_send_message_in_stub(self):
        chat_post = {\
            "access_token": self.access_token,
            "text": "Hello.",
            "activity_id": 1,
        }
        rsp =  self.client.post("/api/chat/", chat_post)
        print rsp.content
        self.assertEquals(200, rsp.status_code)
    """

    def test_send_message(self):
        ios_notifications_models = handlers.push_models
        utils_module = handlers.utils

        handlers.push_models = mock.MagicMock()
        handlers.utils = mock.MagicMock()
        handlers.utils.get_client_ip.return_value = "127.0.0.1"
        hd = handlers.ChatHandler()
        request = mock.MagicMock()
        request.user = User.objects.get(username='test')
        request.POST = {"activity_id": 1, "text": "First chat message."}

        def mock_and_assert_send_notification(devices, service, notification):
            self.assertEquals(2, len(devices))

        original_send_notification = handlers.send_notification
        handlers.send_notification = mock_and_assert_send_notification
        rsp = hd.create(request)
        handlers.send_notification = original_send_notification

        chat = Chat.objects.get(text="First chat message.")
        self.assertNotEquals(None, chat)

        handlers.push_models = ios_notifications_models
        handlers.utils = utils_module


class UtilsTest(TestCase):
    def test_copy_file(self):
        import tempfile
        dest = tempfile.NamedTemporaryFile("w")
        src  = file("resources/10x10.png", "r")
        
        utils.copy_file(src, dest)
        self.assertEquals(os.stat(src.name).st_size, os.stat(dest.name).st_size)

        dest.close()
        src.close()
