"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import simplejson
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from pdb import Pdb, set_trace as bp
from models import Message, Activity
import os
import utils

class ActivityTest(TestCase):
    fixtures = ['users', 'activity.json', 'ios_notifications.json']

    def test_devices(self):
        devices = Activity.objects.get(pk=1).devices("dev")
        self.assertEquals(3, len(devices))
        self.assertEquals("dev", devices[0].service.name)

class OAuthTestCase(TestCase):
    @override_settings(DEBUG=True)
    def setUp(self):
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

class ChatTest(TestCase):
    @override_settings(DEBUG=True)
    def setUp(self):
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

    def test_send_message(self):
        send_message_fields = {\
            "activity_id": 1,
            "text": "First sended chat message."
        }
        rsp = self.client.post('/api/chat/',  send_message_fields)
        self.assertEquals(201, rsp.status_code)

class UtilsTest(TestCase):
    def test_copy_file(self):
        import tempfile
        dest = tempfile.NamedTemporaryFile("w")
        src  = file("resources/10x10.png", "r")
        
        utils.copy_file(src, dest)
        self.assertEquals(os.stat(src.name).st_size, os.stat(dest.name).st_size)

        dest.close()
        src.close()
