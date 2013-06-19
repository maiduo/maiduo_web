"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from qiniu_stub.operator import ImageThumbnailOperator,\
                                ImageThumbnailCenterMode,\
                                ImageThumbnailNormalMode

class ImageThumbnailOperatorTest(TestCase):
    def test_image_operate(self):
        operator = ImageThumbnailOperator("imageView/2/w/200/h/200")

        assert ImageThumbnailNormalMode == operator.mode
        assert 200 == operator.width
        assert 200 == operator.height

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
