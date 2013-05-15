from django.contrib import admin
from models import Activity, Chat

class ActivityAdmin(admin.ModelAdmin):
    pass

class ChatAdmin(admin.ModelAmin):
    pass

admin.site.register(Activity, ActivityAdmin)
admin.site.register(Chat, ChatAdmin)
