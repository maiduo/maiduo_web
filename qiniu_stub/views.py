#! -*- encoding:utf-8 -*-

import os
import token
from qiniu_stub.models import Credential, Key
from django.http import HttpResponse
from django.conf import settings
from django.views.static import serve
from os.path import join, basename, dirname, exists, splitext
from operator import ImageThumbnailOperator
from models import ServerPutToken
from pdb import set_trace as bp

QINIU_MEDIA_ROOT = join(settings.MEDIA_ROOT, "qiniu")


def upload(request):
    key = request.POST.get("key", "")
    try:
        server_token = ServerPutToken(request.POST.get("token"))
    except token.SignAuthenticateFault, e:
        print e

    bucket = server_token.put_token.scope.bucket
    f = request.FILES.get('file')
    upload_dirname = dirname(join(QINIU_MEDIA_ROOT, bucket, key))

    if not exists(upload_dirname):
        os.makedirs(upload_dirname)
    

    obj = open(join(QINIU_MEDIA_ROOT, bucket, key), "w")
    for chunk in f.chunks():
        obj.write(chunk)
    obj.close()

    return HttpResponse("")

def download(request, bucket, path):
    query_string = request.META.get("QUERY_STRING")
    no_operator = "" == query_string
    if no_operator:
        key = path
    else:
        operator = ImageThumbnailOperator(query_string)
        operator.process(path, join(QINIU_MEDIA_ROOT, bucket))

        bp()
        key = operator.cache_key(path)

    return serve(request, key, join(QINIU_MEDIA_ROOT, bucket))
