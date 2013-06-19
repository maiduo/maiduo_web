"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
from os.path import dirname, abspath, join, exists
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from qiniu_stub.operator import ImageThumbnailOperator,\
                                ImageThumbnailCenterMode,\
                                ImageThumbnailNormalMode
from StringIO import StringIO

class ImageThumbnailOperatorTest(TestCase):
    def test_image_operate(self):
        operator = ImageThumbnailOperator("imageView/2/w/200/h/200")

        assert ImageThumbnailNormalMode == operator.mode
        assert 200 == operator.width
        assert 200 == operator.height
        assert "2_200_200_100", operator.cache_id

    def test_image_operate_not_has_height(self):
        operator = ImageThumbnailOperator("imageView/2/w/200")

        assert ImageThumbnailNormalMode == operator.mode
        assert 200 == operator.width
        assert 0 == operator.height

    def test_image_operate_not_has_width(self):
        operator = ImageThumbnailOperator("imageView/2/h/200")

        assert ImageThumbnailNormalMode == operator.mode
        assert 0 == operator.width
        assert 200 == operator.height

FIXTURE_DIR = abspath(join(dirname(__file__), "fixtures"))

class QiniuStubTest(TestCase):
    def setUp(self):
        self.client = Client()

        import shutil
        dest = join(settings.MEDIA_ROOT, "qiniu/jpg/13/6/19")
        if not exists(dest):
            os.makedirs()
        shutil.copyfile(join(FIXTURE_DIR, "10x10.jpg"),\
                        join(settings.MEDIA_ROOT, "qiniu/jpg/13/6/19/10x10.jpg"))

    def test_upload(self):
        upload_url = reverse("qiniu_stub_upload")
        key = "txt/13/6/19/hello.txt"
        request = {\
            "file": file(join(FIXTURE_DIR, "txt/13/6/19/hello.txt"), "r"),
            "key": key
        }

        rsp = self.client.post(upload_url, request)
        assert 200, rsp.status_code

        assert True, exists(join(settings.MEDIA_ROOT, key))

    def test_download(self):
        op = "imageView/2/w/200/h/200"
        key = "jpg/13/6/19/10x10.jpg"
        download_url = "%s?%s" % (\
            reverse("qiniu_stub_download", args = ("maiduo", key,)), op)
        rsp = self.client.get(download_url)
        print rsp.content
        assert 200 == rsp.status_code

