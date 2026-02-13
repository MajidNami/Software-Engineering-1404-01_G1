import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, Attachment, BlockList, PrivateChat

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    
    # --- 1. CONNECTION LOGIC ---
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Reject if user is not authenticated
        if self.user.is_anonymous:
            await self.close()
            return

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Set user status to Online
        await self.update_user_status(True)
        
        await self.accept()

    async def disconnect(self, close_code):
        # Set user status to Offline and update Last Seen
        await self.update_user_status(False)

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # --- 2. RECEIVE LOGIC (Action Router) ---
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', 'message') # message, delete, or typing

        # A. HANDLE DELETION
        if action == 'delete':
            msg_id = data.get('msg_id')
            if await self.delete_message_db(msg_id):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'msg_id': msg_id
                    }
                )
            return

        # B. HANDLE TYPING INDICATOR
        if action == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', True)
                }
            )
            return

        # C. HANDLE NEW MESSAGE / REPLY
        if action == 'message':
            # Check if there is a block between users (Private Chat only)
            if await self.is_blocked_check():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Message failed: You or the recipient is blocked.'
                }))
                return

            message_text = data.get('message', '')
            file_id = data.get('file_id')
            reply_to_id = data.get('reply_to_id')

            # Save to Database
            saved_msg = await self.save_message(message_text, reply_to_id, file_id)

            # Broadcast to Group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_id': saved_msg.msg_id,
                    'message': message_text,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'reply_to_id': reply_to_id,
                    'attachment_url': await self.get_attachment_url(saved_msg),
                    'timestamp': str(saved_msg.timestamp)
                }
            )

    # --- 3. EVENT HANDLERS (Sending to individual WebSockets) ---
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps(event))


    # --- 4. DATABASE SYNC METHODS (The "Bridges") ---

    @database_sync_to_async
    def update_user_status(self, is_online):
        User.objects.filter(id=self.user.id).update(
            is_online=is_online,
            last_seen=timezone.now()
        )

    @database_sync_to_async
    def is_blocked_check(self):
        try:
            room = ChatRoom.objects.get(chat_id=self.room_id)
            if room.chat_type == 'private':
                p_info = room.private_info
                other_user = p_info.user2 if p_info.user1 == self.user else p_info.user1
                
                # Check if a block exists in either direction
                return BlockList.objects.filter(
                    (Q(blocker=self.user) & Q(blocked=other_user)) |
                    (Q(blocker=other_user) & Q(blocked=self.user))
                ).exists()
            return False
        except: return False

    @database_sync_to_async
    def save_message(self, content, reply_to_id=None, file_id=None):
        room = ChatRoom.objects.get(chat_id=self.room_id)
        reply_to_obj = Message.objects.get(msg_id=reply_to_id) if reply_to_id else None
        
        msg = Message.objects.create(
            sender=self.user,
            chat=room,
            content=content,
            reply_to=reply_to_obj
        )

        # If a file was uploaded via API earlier, link it to this message now
        if file_id:
            Attachment.objects.filter(file_id=file_id).update(message=msg)
        
        # Update ChatRoom "updated_at" to bump it to top of inbox
        room.updated_at = timezone.now()
        room.save()
        return msg

    @database_sync_to_async
    def delete_message_db(self, msg_id):
        try:
            msg = Message.objects.get(msg_id=msg_id, sender=self.user)
            msg.is_deleted = True
            msg.save() 
            return True 
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def get_attachment_url(self, msg):
        attachment = msg.attachments.first() # related_name from models
        return attachment.file_url.url if attachment else None