from django.conf.urls import patterns, url
from piston.resource import Resource
from handlers import MessageHandler
from oauthost.utils import PistonAuthHelper
import oauthost.urls
# 
message_handler = Resource(MessageHandler, \
                           authentication=PistonAuthHelper(None))
urlpatterns = oauthost.urls.urlpatterns + patterns('',
    url(r'^message/', message_handler) #, {'emitter_format': 'json'}),
)
