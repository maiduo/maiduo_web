from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mdapp.views.home', name='home'),
    # url(r'^mdapp/', include('mdapp.foo.urls')),
    url(r'^aps/', include('ios_notifications.urls')),
    # url(r'^api/', include('oauthost.urls')),
    url(r'^api/', include('md.urls')),
    url(r'^qiniu/', include('mock_qiniu.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
