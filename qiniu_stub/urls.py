from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^upload/$', 'qiniu_stub.views.upload', name='qiniu_stub_upload'),
    url(r'^(?P<bucket>\w+)/(?P<path>.+)', 'qiniu_stub.views.download', \
        name='qiniu_stub_download'),
)
