from django.conf.urls import patterns, url
from piston.resource import Resource
from handlers import MessageHandler, ChatHandler, ChatsHandler, UserHandler,\
                     AuthenticationHandler, ActivityHandler,\
                     MessageAddonHandler, MessagesHandler, MessageStashHandler,\
                     ActivityInviteHandler, LogoutHandler, ProfileHandler
from oauthost.utils import PistonAuthHelper
import oauthost.urls

auth = PistonAuthHelper(None)
message_handler = Resource(MessageHandler, authentication= auth)
message_stash_handler = Resource(MessageStashHandler, authentication=auth)
messages_handler = Resource(MessagesHandler, authentication=auth)
message_addon_handler = Resource(MessageAddonHandler, authentication=auth)
chat_handler = Resource(ChatHandler, authentication=auth)
chats_handler = Resource(ChatsHandler, authentication=auth)
user_handler = Resource(UserHandler)
profile_handler = Resource(ProfileHandler, authentication=auth)
invite_handler = Resource(ActivityInviteHandler, authentication=auth)
authentication_handler = Resource(AuthenticationHandler)
logout_handler = Resource(LogoutHandler, authentication=auth)
activity_handler = Resource(ActivityHandler, authentication=auth)

urlpatterns = oauthost.urls.urlpatterns + patterns('',
    # url(r'^authentication/$', 'oauthost.auth_views.endpoint_token',\
    #    name='oauthost_token'),
    url(r'^authentication/$', authentication_handler), 
    url(r'^logout/$', logout_handler),
    url(r'^user/$', user_handler),
    url(r'^user/(?P<username>[^/]+)/$', user_handler),
    url(r'^profile/', profile_handler),
    url(r'^message/$', message_handler),
    url(r'^message/stash/$', message_stash_handler),
    url(r'^message/addon/$', message_addon_handler),
    url(r'^messages/(?P<activity_id>[^/]+)/$', messages_handler),
    url(r'^chat/$', chat_handler),
    url(r'^chat/(?P<chat_id>[^/]+)/$', chat_handler),
    url(r'^chats/(?P<activity_id>[^/]+)/$', chats_handler),
    url(r'^activity/$', activity_handler),
    url(r'^activity/invite/$', invite_handler),
)
