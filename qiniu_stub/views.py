import os
from django.http import HttpResponse
from django.conf import settings
from django.views.static import serve
from os.path import join, basename, dirname, exists, splitext
from operator import ImageThumbnailOperator
from pdb import set_trace as bp

QINIU_MEDIA_ROOT = join(settings.MEDIA_ROOT, "qiniu")

def upload(request):
    key = request.POST.get("key", "")
    f = request.FILES.get('file')
    upload_dirname = dirname(join(QINIU_MEDIA_ROOT, key))
    upload_basename = basename(key)

    
    if not exists(upload_dirname):
        os.makedirs(upload_dirname)
    
    obj = open(join(QINIU_MEDIA_ROOT, key), "w")
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
        operator.process(path, QINIU_MEDIA_ROOT)

        key = operator.cache_key(path)

    return serve(request, key, QINIU_MEDIA_ROOT)
