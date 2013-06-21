# -*- encoding:utf-8 -*-

from PIL import Image
from pdb import set_trace as bp
from os.path import join, basename, dirname, exists, splitext


class ImageThumbnailCenterMode:
    pass

class ImageThumbnailNormalMode:
    pass

class ImageThumbnailMode:
    @staticmethod
    def create(mode):
        mode = int(mode)
        if 1 == mode:
            return ImageThumbnailCenterMode
        elif 2 == mode:
            return ImageThumbnailNormalMode

class ImageThumbnailOperator(object):
    _map_methods = {\
        "q": "set_quality",
        "format": "set_format",
        "w": "set_width_or_height",
        "h": "set_width_or_height",
    }

    def __init__(self, op = ""):
        self.width = self.height = 0
        self.quality = 100
        self.format = None

        if not op.startswith("imageView"):
            return 

        ops = op.split("/")
        self.mode = ImageThumbnailMode.create(ops[1])

        for i in range(1, 10):
            start = i * 2
            end = start + 2
            kv = ops[start:end]

            try:
                method = self._map_methods.get(kv[0])
                getattr(self, method)(kv)
            except IndexError:
                break

    def set_quality(self, kv):
        self.quality = int(kv[1])

    def set_format(self, kv):
        self.format = kv[1]

    def set_width_or_height(self, size):
        if "w" == size[0]:
            attr = "width"
        elif "h" == size[0]:
            attr = "height"

        setattr(self, attr, int(size[1]))

    @property
    def cache_id(self):
        if self.mode == ImageThumbnailNormalMode:
            number_mode = 2
        elif self.mode == ImageThumbnailCenterMode:
            number_mode = 1

        return "%d_%s_%s_%s" % (number_mode, self.width, self.height,\
                                self.quality)

    def cache_key(self, key):
        key_dirname = dirname(key)
        filename, fileext = splitext(basename(key))
        if self.format:
            fileext = self.format

        return join(key_dirname,\
                    "%s_%s%s" % (filename, self.cache_id, fileext))


    def calculate(self, size):
        width = float(size[0])
        height = float(size[1])
        except_width = self.width
        except_height = self.height

        rate = except_width / width

        zoomed_width = width * rate
        zoomed_height = height * rate

        except_too_long = zoomed_height < except_height
        if except_too_long:
            rate = except_height / height

        zoomed_height = height * rate
        zoomed_width = width * rate

        if not except_width:
            except_width = width * rate
        elif not except_height:
            except_height = height * rate

        if self.mode == ImageThumbnailCenterMode:
            x = (zoomed_width - except_width) / 2
            y = (zoomed_height - except_height) / 2
        else:
            x = y = 0

        return (x, y, except_width, except_height, rate)


    def process(self, file, document_root):
        img = Image.open(join(document_root, file))

        rect = caculate(img.size())

