from django.contrib import admin
from models import Activity, Chat, Message, MessageAddon

class ActivityAdmin(admin.ModelAdmin):
    pass

class ChatAdmin(admin.ModelAdmin):
    pass

class MessageAdmin(admin.ModelAdmin):
    pass

class MessageAddonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageAddon, MessageAddonAdmin)
