from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^aps/', include('ios_notifications.urls')),
    url(r'^api/', include('md.urls')),
    url(r'^qiniu/', include('qiniu_stub.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
