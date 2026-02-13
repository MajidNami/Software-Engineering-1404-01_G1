from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, PrivateChat, GroupChat, ChatParticipant, Message, Attachment

User = get_user_model()

from .models import (
    ChatRoom, PrivateChat, GroupChat,
    ChatParticipant, Message, Attachment
)

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic', 'bio', 'is_online', 'last_seen']

class ChatParticipantSerializer(serializers.ModelSerializer):
    user_details = UserBasicSerializer(source='user', read_only=True)
    class Meta:
        model = ChatParticipant
        fields = ['id', 'user', 'user_details', 'is_admin', 'is_muted']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file_id', 'file', 'file_type', 'file_size']

class MessageSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    sender_details = UserBasicSerializer(source='sender', read_only=True)
    class Meta:
        model = Message
        fields = ['msg_id', 'sender', 'sender_details', 'chat', 'content', 'type_str', 'timestamp', 'is_read', 'attachments']

class PrivateChatSerializer(serializers.ModelSerializer):
    user1_details = UserBasicSerializer(source='user1', read_only=True)
    user2_details = UserBasicSerializer(source='user2', read_only=True)
    class Meta:
        model = PrivateChat
        fields = ['user1', 'user2', 'user1_details', 'user2_details']

class GroupChatSerializer(serializers.ModelSerializer):
    admin_details = UserBasicSerializer(source='admin', read_only=True)
    class Meta:
        model = GroupChat
        fields = ['group_name', 'group_image', 'admin', 'admin_details', 'bio']

class GroupChatUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['group_name', 'group_image', 'bio']

class ChatRoomSerializer(serializers.ModelSerializer):
    private_info = PrivateChatSerializer(read_only=True)
    group_info = GroupChatSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['chat_id', 'created_at', 'updated_at', 'chat_type', 'private_info', 'group_info', 'last_message', 'current_user_role']

    def get_last_message(self, obj):
        last_msg = obj.chat_messages.order_by('-timestamp').first()
        return MessageSerializer(last_msg, context=self.context).data if last_msg else None

    def get_current_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            p = ChatParticipant.objects.filter(chat=obj, user=request.user).first()
            return {'is_admin': p.is_admin, 'is_muted': p.is_muted} if p else None
        return None
    



class NotificationSerializer(serializers.ModelSerializer):
    sender_details = UserBasicSerializer(source='sender', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_details',
            'notification_type', 'title', 'body', 'data',
            'is_read', 'is_seen', 'created_at', 'time_ago'
        ]
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        import math
        
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f"{delta.days} روز پیش"
        elif delta.seconds >= 3600:
            return f"{math.floor(delta.seconds / 3600)} ساعت پیش"
        elif delta.seconds >= 60:
            return f"{math.floor(delta.seconds / 60)} دقیقه پیش"
        else:
            return "چند لحظه پیش"




class WebPushSubscriptionSerializer(serializers.Serializer):
    subscription = serializers.JSONField()
    
    def update(self, instance, validated_data):
        instance.web_push_subscription = validated_data.get('subscription')
        instance.save()
        return instance    
