from django.conf.urls import patterns, url
from piston.resource import Resource
from handlers import MessageHandler, ChatHandler, ChatsHandler, UserHandler
from oauthost.utils import PistonAuthHelper
import oauthost.urls

auth = PistonAuthHelper(None)
message_handler = Resource(MessageHandler, authentication= auth)
chat_handler = Resource(ChatHandler, authentication=auth)
chats_handler = Resource(ChatsHandler, authentication=auth)
user_handler = Resource(UserHandler)
urlpatterns = oauthost.urls.urlpatterns + patterns('',
    url(r'^authentication/$', 'oauthost.auth_views.endpoint_token',\
        name='oauthost_token'),
    url(r'^user/$', user_handler),
    url(r'^user/(?P<user_id>[^/]+)/$', user_handler),
    url(r'^message/$', message_handler),
    url(r'^chat/$', chat_handler),
    url(r'^chats/$', chats_handler),
)
