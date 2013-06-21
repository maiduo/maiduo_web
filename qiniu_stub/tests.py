
#! -*- encoding:utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import token
import shutil
import tempfile
from models import ServerPutToken
from os.path import dirname, basename, abspath, join, exists
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from qiniu_stub.operator import ImageThumbnailOperator,\
                                ImageThumbnailCenterMode,\
                                ImageThumbnailNormalMode
from pdb import set_trace as bp
from StringIO import StringIO
from PIL import Image


FIXTURE_DIR = abspath(join(dirname(__file__), "fixtures"))

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

    def test_calculate_center(self):
        operator = ImageThumbnailOperator("imageView/1/w/50/h/50")
        rect = operator.calculate((100, 110))
        assert (0, 2.5, 50, 50, 0.5) == rect
        rect = operator.calculate((110, 100))
        assert (2.5, 0, 50, 50, 0.5) == rect
        operator = ImageThumbnailOperator("imageView/1/w/40/h/50")
        rect = operator.calculate((120, 100))
        assert (10, 0, 40, 50, 0.5) == rect

    def test_calculate_normal(self):
        operator = ImageThumbnailOperator("imageView/2/w/50/h/50")
        rect = operator.calculate((100, 100))
        assert (0, 0, 50, 50, 0.5) == rect

        operator = ImageThumbnailOperator("imageView/2/w/50/h/100")
        rect = operator.calculate((100, 100))
        assert (0, 0, 50, 100, 1) == rect


    def test_calculate_normal_only_width(self):
        operator = ImageThumbnailOperator("imageView/2/w/50")
        rect = operator.calculate((100, 100))
        assert (0, 0, 50, 50, 0.5) == rect

    def test_calculate_normal_only_height(self):
        operator = ImageThumbnailOperator("imageView/2/h/50")
        rect = operator.calculate((100, 100))
        assert (0, 0, 50, 50, 0.5) == rect

    def test_calculate_normal_zoomout(self):
        operator = ImageThumbnailOperator("imageView/2/h/200")
        rect = operator.calculate((100, 100))
        assert (0, 0, 200, 200, 2) == rect

    def test_calculate_normal_width_zoomout(self):
        operator = ImageThumbnailOperator("imageView/2/w/200/h/100")
        rect = operator.calculate((100, 100))
        assert (0, 0, 200, 100, 2) == rect

    def test_calculate_normal_height_zoomout(self):
        operator = ImageThumbnailOperator("imageView/2/w/100/h/200")
        rect = operator.calculate((100, 100))
        assert (0, 0, 100, 200, 2) == rect

    def test_process(self):
        destination = tempfile.NamedTemporaryFile()
        destination_path = destination.name
        source_file = join(FIXTURE_DIR, "100x100.jpg")
        shutil.copyfile(source_file, destination_path)
        
        operator = ImageThumbnailOperator("imageView/2/w/50/h/50")
        operator.process(basename(destination_path), dirname(destination_path)) 

        # 改进
        # 在内存中完成，不做真实的文件IO读写操作
        img = Image.open(destination_path)
        assert (50, 50) == img.size

class QiniuStubViewTest(TestCase):
    fixtures = ['credential.json']
    def setUp(self):
        self.client = Client()
        self.bucket = "maiduo"

        dest = join(settings.MEDIA_ROOT, "qiniu/", self.bucket, "jpg/13/6/19")
        if not exists(dest):
            os.makedirs(dest)

        dest_file = join(settings.MEDIA_ROOT, dest, "10x10.jpg")
        if not exists(dest_file):
            shutil.copyfile(join(FIXTURE_DIR, "10x10.jpg"), dest_file)

    def test_upload(self):
        upload_url = reverse("qiniu_stub_upload")
        key = "txt/13/6/19/hello.txt"
        put_token = token.RequestPutToken("11111", "11111",\
                                           token.Scope.create(self.bucket))
        put_token = put_token.encode(put_token.json)
        request = {\
            "file": file(join(FIXTURE_DIR, "txt/13/6/19/hello.txt"), "r"),
            "key": key,
            "token": put_token,
        }

        rsp = self.client.post(upload_url, request)
        assert 200, rsp.status_code

        assert True, exists(join(settings.MEDIA_ROOT,\
                                 'maiduo/txt/13/6/19/hello.txt'))

    def test_download(self):
        op = "imageView/2/w/200/h/200"
        key = "jpg/13/6/19/10x10.jpg"
        download_url = "%s?%s" % (\
            reverse("qiniu_stub_download", args = (self.bucket, key,)), op)

        rsp = self.client.get(download_url)
        print rsp.content
        assert 200 == rsp.status_code

class PascalToCamelCaseTest(TestCase):
    def test_pascal_to_camel_case(self):
        assert "yourName" == token.pascal_to_camel_case("your_name")
        assert "name" == token.pascal_to_camel_case("name")
        assert "youAreWelcome" == token.pascal_to_camel_case("you_are_welcome")

class TokenTest(TestCase):
    def setUp(self):
        self.token = token.Token("11111", "11111")
        self.token2 = token.Token("00000", "00000")

    def test_check(self):
        access, signature, content = self.token.encode("check").split(":")
        assert True == self.token.check(signature, content)

    def test_check_fault(self):
        access, signature, content = self.token2.encode("check").split(":")
        assert False == self.token.check(signature, content)


class RequestPutTokenTest(TestCase):
    def setUp(self):
        self.put_token = self.create_token("11111", "11111")

    def create_token(self, access, secret):
        scope = token.Scope("maiduo")
        return token.RequestPutToken(access, secret, scope, callback_url="0",\
                              callback_body_type="0", customer="0",\
                              async_ops="0", escape="0", detect_mine="0")


    def test_dict(self):
        t = self.put_token.dict
        assert "maiduo" == t['scope']
        for field in token.RequestPutToken.JSON_FIELDS_MAP:
            assert True == t.has_key(token.pascal_to_camel_case(field))


    def test_from_json(self):
        t = token\
                .RequestPutToken\
                .from_json(self.put_token.access, self.put_token.secret,\
                           self.put_token.json)

        assert "maiduo" == t.scope.bucket
        assert "" == t.scope.key
        assert "0" == t.callback_url


class ServerPutTokenTest(TestCase):
    fixtures = ['credential.json']


    def setUp(self):
        access = secret = "11111"
        scope = token.Scope.create("maiduo")
        self.put_token = token.RequestPutToken(access, secret, scope,\
                                               callback_url="0",\
                                               callback_body_type="0",\
                                               customer="0", async_ops="0",\
                                               escape="0", detect_mine="0")



    def test_init(self):
        put_token = self.put_token
        server_token = ServerPutToken(put_token.encode(put_token.json))

        assert True==True

