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
from ios_notifications.models import Device
from models import Message, Activity, Chat
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

class ActivityTest(TestCase):
    #fixtures = ['users', 'activity.json', 'ios_notifications.json']

    def test_devices(self):
        devices = Activity.objects.get(pk=1).devices("dev")
        self.assertEquals(3, len(devices))
        self.assertEquals("dev", devices[0].service.name)

class ActivityHandlerTest(OAuthTestCase):
    def test_read(self):
        activity_url = '/api/activity/?access_token=%s' % self.access_token
        rsp = self.client.get(activity_url)
        activities = simplejson.loads(rsp.content)
        self.assertEquals(200, rsp.status_code)
        self.assertEquals(1, len(activities))
        self.assertEquals(1, activities[0]['owner']['id'])


    def test_create(self):
        activity_subject_name = "The second activity."
        request_data = {
            "subject": activity_subject_name,
            "access_token": self.access_token
        }
        rsp = self.client.post('/api/activity/', request_data)
        print rsp.content
        self.assertEquals(200, rsp.status_code)

        activity = Activity.objects.get(subject=subject)
        self.assertEquals(activity_subject_name, activity.subject)

class UserTest(TestCase):
    
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        user_data = {\
            "username": "13000000000",
            "password": "13000000000"
        }
        rsp = self.client.post('/api/user/', user_data)
        self.assertEquals(200, rsp.status_code)
        print rsp.content

        user = User.objects.get(username="13000000000")
        self.assertNotEquals(None, user)

class MessageTest(OAuthTestCase):
    fixtures = ['users', 'oauthost.json', 'activity.json']

    def test_create_text_message(self):
        message_fields = {\
            "body": "The first.",
            'access_token': self.access_token,
            'activity_id': 1,
        }

        rsp = self.client.post('/api/message/', message_fields)
        self.assertEquals(201, rsp.status_code)

        msg = Message.objects.get(body="The first.")
        self.assertEquals("The first.", msg.body)

    def test_create_text_message_empty_activity_id_and_subject(self):
        message_fields = {\
            "body": "The second.",
            'access_token': self.access_token,
        }

        rsp = self.client.post('/api/message/', message_fields)
        self.assertEquals(201, rsp.status_code)

        msg = Message.objects.get(body="The second.")
        self.assertEquals("The second.", msg.body)
        
        activity = Activity.objects.get(subject=msg.body)


    def test_create_message_and_activity(self):
        message_fields = {\
            "activity_subject": "The first activity.",
            "body": "The first.",
            'access_token': self.access_token,
            "addons": open("resources/10x10.png")
        }

        rsp = self.client.post('/api/message/', message_fields)
        self.assertEquals(201, rsp.status_code)

        msg = Message.objects.get(body="The first.")
        self.assertEquals("The first.", msg.body)

class HandlerTest(TestCase):
    def test_send_notification_with_token(self):
        handlers.push_models = mock.MagicMock()
        handlers.send_notification([], "dev", mock.MagicMock())

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
                                

    @override_settings(DEBUG=True)
    def test_authenticate(self):
        request_token = {\
            'client_id': '2dc5d858f1f441aa8e957b82ce248816',
            'username': 'test',
            'password': '123123',
            'grant_type': 'password',
            'scope': '',
            'device_token': '<token>',
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

class ChatTest(TestCase):
    fixtures = ['users', 'activity.json', 'ios_notifications.json']

    def test_send_message(self):
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
        hd.create(request)
        handlers.send_notification = original_send_notification

        chat = Chat.objects.get(text="First chat message.")
        self.assertNotEquals(None, chat)


class UtilsTest(TestCase):
    def test_copy_file(self):
        import tempfile
        dest = tempfile.NamedTemporaryFile("w")
        src  = file("resources/10x10.png", "r")
        
        utils.copy_file(src, dest)
        self.assertEquals(os.stat(src.name).st_size, os.stat(dest.name).st_size)

        dest.close()
        src.close()
