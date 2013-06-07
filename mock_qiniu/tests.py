"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_key(self):
        key_url = reverse("mock_qiniu.key")
        request = {\
            "key": "hi",
            "file": file("mock_qiniu/fixtures/hi")
        }
        rsp = self.client.post(key_url, request)
        print rsp.content
