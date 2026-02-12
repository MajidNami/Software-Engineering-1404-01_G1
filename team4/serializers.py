from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ChatRoom, PrivateChat, GroupChat, 
    ChatParticipant, Message, Attachment, 
    BlockList, UserReport
)

User = get_user_model()

# --- THIS ONE MUST BE FIRST ---
class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic_url', 'is_online', 'last_seen']

# --- This one uses the one above ---
class ChatParticipantSerializer(serializers.ModelSerializer):
    user_details = UserBasicSerializer(source='user', read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['user', 'user_details', 'is_muted', 'is_admin']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    sender_details = UserBasicSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = [
            'msg_id', 'sender', 'sender_details', 'chat', 'content', 
            'type_str', 'timestamp', 'is_read', 'is_deleted', 
            'is_saved', 'reply_to', 'attachments'
        ]

class PrivateChatSerializer(serializers.ModelSerializer):
    user1_details = UserBasicSerializer(source='user1', read_only=True)
    user2_details = UserBasicSerializer(source='user2', read_only=True)
    
    class Meta:
        model = PrivateChat
        fields = ['user1', 'user2', 'user1_details', 'user2_details']

class GroupChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['group_name', 'group_image', 'admin']

class ChatRoomSerializer(serializers.ModelSerializer):
    private_info = PrivateChatSerializer(read_only=True)
    group_info = GroupChatSerializer(read_only=True)
    
    # FIX: Removed source='members' because the variable name is already 'members'
    members = ChatParticipantSerializer(many=True, read_only=True) 
    
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'chat_id', 
            'created_at', 
            'updated_at', 
            'chat_type', 
            'private_info', 
            'group_info', 
            'members', 
            'last_message'
        ]



    def get_last_message(self, obj):
        # We use .chat_messages because that's the related_name we set in models.py
        last_msg = obj.chat_messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockList
        fields = '__all__'

class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReport
        fields = '__all__'