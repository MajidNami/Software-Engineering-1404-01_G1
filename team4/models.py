from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class ChatRoom(models.Model):
    chat_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Chat {self.chat_id} ({self.chat_type})"

class PrivateChat(models.Model):
    chat = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, primary_key=True, related_name='private_info')
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_2')

class GroupChat(models.Model):
    chat = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, primary_key=True, related_name='group_info')
    group_name = models.CharField(max_length=255)
    group_image = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_groups')

class ChatParticipant(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participants')
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='members')
    is_muted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

class Message(models.Model):
    msg_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    type_str = models.CharField(max_length=50, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

class Attachment(models.Model):
    file_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file_url = models.TextField()
    file_type = models.CharField(max_length=50)
    file_size = models.FloatField()

class BlockList(models.Model):
    id = models.AutoField(primary_key=True)
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocking_users')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_users')
    created_at = models.DateTimeField(auto_now_add=True)

class UserReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_submitted')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_against')
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)



class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_pic_url = models.URLField(max_length=500, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username