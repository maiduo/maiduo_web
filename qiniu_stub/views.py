import os
from django.http import HttpResponse
from django.conf import settings
from os.path import join, basename, dirname, exists
from pdb import set_trace as bp

def upload(request):
    key = request.POST.get("key", "")
    f = request.FILES.get('file')
    qiniu_upload_dir = join(settings.MEDIA_ROOT, "qiniu")
    upload_dirname = dirname(join(qiniu_upload_dir, key))
    upload_basename = basename(key)

    
    if not exists(upload_dirname):
        os.makedirs(upload_dirname)
    
    obj = open(join(qiniu_upload_dir, key), "w")
    for chunk in f.chunks():
        obj.write(chunk)
    obj.close()

    return HttpResponse("")

def download(request, bucket, path):
    pass
