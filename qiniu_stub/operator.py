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

    def process(self):
        pass
