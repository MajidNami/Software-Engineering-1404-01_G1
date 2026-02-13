from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ChatRoom, PrivateChat, GroupChat, Message, ChatParticipant , User

admin.site.register(ChatRoom)
admin.site.register(PrivateChat)
admin.site.register(GroupChat) 
admin.site.register(Message)
admin.site.register(ChatParticipant)

class CustomUserAdmin(UserAdmin):
    model = User
    # This adds our custom fields to the list view in the admin
    list_display = ['id' , 'username', 'email', 'is_online', 'last_seen', 'is_staff']
    
    # This adds the custom fields to the 'Edit User' page
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Profile Info', {'fields': ('bio', 'profile_pic_url', 'is_online')}),
    )

admin.site.register(User, CustomUserAdmin)