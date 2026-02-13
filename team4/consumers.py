import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from users.services import NotificationService
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            self.user = self.scope['user']

            if not self.user.is_authenticated:
                await self.close()
                return

            # عضویت در گروه
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # تغییر وضعیت به آنلاین در دیتابیس
            await self.update_user_status(True)

            await self.accept()

            # ارسال پیام به گروه که این کاربر آنلاین شد
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'status': 'online',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
            
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # تغییر وضعیت به آفلاین
            if self.user.is_authenticated:
                await self.update_user_status(False)
                
                # ارسال پیام آفلاین شدن به گروه
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_status',
                        'status': 'offline',
                        'user_id': self.user.id,
                        'username': self.user.username
                    }
                )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            msg_type = data.get('type', 'chat_message')
            user = self.scope['user']
            
            print(f"🔵 ChatConsumer.receive() called - Type: {msg_type}, User: {user.username}")

            if not user.is_authenticated:
                print("🔴 User not authenticated")
                return

            if msg_type == 'chat_message':
                message_content = data.get('message', '')
                print(f"📝 Text message received: '{message_content}'")
                
                saved_msg = await self.save_message(user, self.room_id, message_content)
                print(f"💾 Message saved: ID={saved_msg.msg_id if saved_msg else 'None'}")
                
                if saved_msg:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_content,
                            'sender_username': user.username,
                            'sender_id': user.id,
                            'msg_id': saved_msg.msg_id,
                            'timestamp': str(saved_msg.timestamp),
                            'type_str': 'text'
                        }
                    )
                    print(f"✅ Message broadcast to group {self.room_group_name}")
                    
                    print(f"🔔 Attempting to send notification for message {saved_msg.msg_id}")
                    await self.send_notification_for_message(saved_msg)
                else:
                    print("🔴 Failed to save message")
                    
            elif msg_type == 'typing':
                print(f"✏️ Typing event: {data.get('is_typing')}")

        except Exception as e:
            print(f"🔴 Error in receive: {e}")
            import traceback
            traceback.print_exc()    
    async def chat_message(self, event):
        response = {
            'type': 'chat_message',
            'message': event.get('message', ''),
            'sender': event.get('sender_username', 'Unknown'),
            'sender_id': event.get('sender_id'),
            'timestamp': event.get('timestamp', ''),
            'msg_id': event.get('msg_id'),
            'type_str': event.get('type_str', 'text'), # audio, image, text
            'is_edited': event.get('is_edited', False)
        }
        if 'file_url' in event:
            response['file_url'] = event['file_url']
            
        await self.send(text_data=json.dumps(response))
    
    
    async def message_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_updated',
            'msg_id': event['msg_id'],
            'new_content': event['new_content'],
            'is_edited': True
        }))

    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'msg_id': event['msg_id']
        }))

    # هندلر وضعیت آنلاین/آفلاین
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'status': event['status'],
            'user_id': event['user_id'],
            'username': event['username']
        }))

    # هندلر تایپینگ
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'is_typing': event['is_typing'],
            'sender': event['sender_username'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        room = ChatRoom.objects.filter(chat_id=room_id).first()
        if room:
            return Message.objects.create(sender=user, chat=room, content=content)
        return None

    @database_sync_to_async
    def update_user_status(self, is_online):
        self.user.is_online = is_online
        self.user.save()

    @database_sync_to_async
    def send_notification_for_message(self, message):
    
        try:
            from users.services import NotificationService
            room = message.chat
        # exclude_user_id = خود فرستنده
            NotificationService.notify_new_message(message, room, message.sender.id)
            print(f"✅ Notification sent for text message {message.msg_id}")
        except Exception as e:
            print(f"❌ Error sending notification for text message: {e}")

    

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # گروه اختصاصی برای نوتیفیکیشن‌های این کاربر
        self.notification_group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # ارسال نوتیفیکیشن‌های خوانده نشده
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'mark_as_read':
            notification_id = data.get('notification_id')
            await self.mark_notification_as_read(notification_id)
        elif action == 'mark_all_as_read':
            await self.mark_all_as_read()
    
    async def send_notification(self, event):
        """ارسال نوتیفیکیشن به کلاینت"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': event['notification']
            }))
            print(f"📨 Notification sent to user {self.user.username}")
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    @database_sync_to_async
    def send_unread_notifications(self):
        """ارسال نوتیفیکیشن‌های خوانده نشده"""
        from users.serializers import NotificationSerializer
        from users.models import Notification
        
        unread_notifications = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        )[:20]
        
    
        pass
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
        except Notification.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_all_as_read(self):
        from .models import Notification
        from django.utils import timezone
        
        Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

    async def send_notification(self, event):
    
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))


    async def chat_list_updated(self, event):
        """بروزرسانی لیست چت‌ها در زمان واقعی"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_list_updated',
                'chat': event['chat']
            }))
            print(f"🔄 Chat list update sent to user {self.user.username}")
        except Exception as e:
            print(f"Error sending chat list update: {e}")


