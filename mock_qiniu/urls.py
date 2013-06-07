from django.conf.urls import patterns, url

urlpatterns = patterns('',\
    url(r'^/$', 'mock_qiniu.views.key', name="mock_qiniu.key"),
)
