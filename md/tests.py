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
from models import Message

class MessageTest(TestCase):
    fixtures = ['users', 'oauthost.json']
    
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

    def test_create_text_message(self):
        message_fields = {\
            "body": "The first.",
            'access_token': self.access_token,
        }

        rsp = self.client.post('/api/message/', message_fields)
        self.assertEquals(201, rsp.status_code)

        msg = Message.objects.get(body="The first.")
        self.assertEquals("The first.", msg.body)
