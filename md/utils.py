#! -*- encoding:utf-8 -*-
from pdb import set_trace as bp

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def copy_file(src, dest):
    while True:
        _buffer = src.read(1024 * 4)
        if not _buffer:
            dest.flush()
            return
        dest.write(_buffer)

def image_resize(fp, width):
    pass

