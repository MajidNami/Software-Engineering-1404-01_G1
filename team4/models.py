from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class ChatRoom(models.Model):
    chat_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_type = models.CharField(max_length=50) # 'private' or 'group'

    def __str__(self):
        return f"Chat {self.chat_id} ({self.chat_type})"

class PrivateChat(models.Model):
    chat = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, primary_key=True, related_name='private_info')
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_2')

class GroupChat(models.Model):
    chat = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, primary_key=True, related_name='group_info')
    group_name = models.CharField(max_length=255)
    group_image = models.ImageField(upload_to='group_images/', blank=True, null=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_groups')
    bio = models.TextField(blank=True, null=True) # بیوگرافی گروه

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
    content = models.TextField(blank=True, null=True)
    type_str = models.CharField(max_length=50, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

class Attachment(models.Model):
    file_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)



class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    web_push_subscription = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.username


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'پیام جدید'),
        ('group_invite', 'دعوت به گروه'),
        ('group_admin', 'ادمین گروه شدید'),
        ('group_removed', 'از گروه حذف شدید'),
        ('mention', 'منشن در گروه'),
        ('reply', 'پاسخ به پیام'),
        ('reaction', 'واکنش به پیام'),
    )

    id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # محتوا
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict)  # اطلاعات اضافی مثل chat_id, message_id, group_id
    
    # وضعیت
    is_read = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)  # دیده شدن در نوتیفیکیشن بار
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"