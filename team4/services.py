from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Notification
import json

User = get_user_model()

class NotificationService:
    
    @staticmethod
    def create_notification(recipient_id, sender_id, notification_type, title, body, data=None):
        """
        ایجاد نوتیفیکیشن در دیتابیس
        """
        try:
            notification = Notification.objects.create(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type=notification_type,
                title=title,
                body=body,
                data=data or {}
            )
            print(f"✅ Notification created: {notification.id} for user {recipient_id}")
            return notification
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def send_realtime_notification(user_id, notification_data):
        """
        ارسال نوتیفیکیشن لحظه‌ای از طریق WebSocket
        """
        try:
            channel_layer = get_channel_layer()
            group_name = f'notifications_{user_id}'
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'notification': notification_data
                }
            )
            print(f"✅ Realtime notification sent to user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error sending realtime notification: {e}")
            import traceback
            traceback.print_exc()
            return False
    
   

    @staticmethod
    def notify_new_message(message, chat_room, exclude_user_id=None):
        
        try:
            print(f"\n{'='*60}")
            print(f"🔔🔔🔔 NOTIFY_NEW_MESSAGE CALLED 🔔🔔🔔")
            print(f"{'='*60}")
            print(f"📨 Message ID: {message.msg_id}")
            print(f"👤 Sender: {message.sender.username} (ID: {message.sender.id})")
            print(f"💬 Content: {message.content[:50] if message.content else 'خالی'}")
            print(f"🏠 Chat Room: {chat_room.chat_id} ({chat_room.chat_type})")
            print(f"📁 Message Type: {message.type_str}")
            print(f"🚫 Exclude User: {exclude_user_id}")
            print(f"{'='*60}")
            
            from .serializers import NotificationSerializer
            from .models import ChatParticipant
            
            # ================ چت خصوصی ================
            if chat_room.chat_type == 'private':
                print(f"\n{'▶️'*10} PRIVATE CHAT NOTIFICATION {'◀️'*10}")
                try:
                    # Get the private chat info
                    private_chat = chat_room.private_info
                    
                    # Find the recipient (the other user)
                    if private_chat.user1.id == message.sender.id:
                        recipient = private_chat.user2
                    else:
                        recipient = private_chat.user1
                        
                    print(f"🎯 Recipient: {recipient.username} (ID: {recipient.id})")
                    
                    # Don't notify the sender
                    if recipient.id == message.sender.id:
                        print("⚠️ Recipient is sender, skipping notification")
                        return
                    
                    # Check if recipient is muted
                    participant = ChatParticipant.objects.filter(
                        chat=chat_room, 
                        user=recipient
                    ).first()
                    
                    if participant and participant.is_muted:
                        print(f"🔇 User {recipient.username} is muted, skipping notification")
                        return
                    
                    # ================ آماده‌سازی متن نوتیفیکیشن بر اساس نوع پیام ================
                    emoji_map = {
                        'text': '💬',
                        'image': '📷',
                        'audio': '🎤',
                        'video': '🎬',
                        'document': '📄',
                        'archive': '📦',
                        'file': '📎'
                    }
                    
                    type_map = {
                        'text': 'پیام',
                        'image': 'تصویر',
                        'audio': 'صدا',
                        'video': 'ویدیو',
                        'document': 'سند',
                        'archive': 'فایل فشرده',
                        'file': 'فایل'
                    }
                    
                    emoji = emoji_map.get(message.type_str, '📎')
                    persian_type = type_map.get(message.type_str, 'فایل')
                    
                    # عنوان نوتیفیکیشن
                    title = f"{emoji} {persian_type} جدید از {message.sender.username}"
                    
                    # متن نوتیفیکیشن
                    if message.type_str == 'text':
                        body = message.content[:100] if message.content else "پیام جدید"
                    elif message.type_str == 'image':
                        body = f"{emoji} تصویر: {message.content or 'بدون توضیحات'}"
                    elif message.type_str == 'audio':
                        body = f"{emoji} پیام صوتی: {message.content or 'ویس'}"
                    elif message.type_str == 'video':
                        body = f"{emoji} ویدیو: {message.content or 'بدون توضیحات'}"
                    elif message.type_str == 'document':
                        body = f"{emoji} سند: {message.content or 'فایل'}"
                    else:
                        body = f"{emoji} فایل: {message.content or 'جدید'}"
                    
                    # اطلاعات اضافی برای دیتا
                    data = {
                        'chat_id': chat_room.chat_id,
                        'chat_type': 'private',
                        'message_id': message.msg_id,
                        'sender_id': message.sender.id,
                        'sender_name': message.sender.username,
                        'sender_username': message.sender.username,
                        'content': message.content[:50] if message.content else None,
                        'message_type': message.type_str,
                        'timestamp': str(message.timestamp),
                        'is_private': True
                    }
                    
                    # اضافه کردن URL فایل اگر وجود دارد
                    try:
                        if message.attachments.exists():
                            attachment = message.attachments.first()
                            data['file_url'] = attachment.file.url
                            data['file_name'] = attachment.file.name.split('/')[-1]
                            data['file_size'] = attachment.file_size
                            print(f"📎 Attachment: {data['file_name']} ({data['file_size']} bytes)")
                    except:
                        pass
                    
                    # Create notification
                    notification = NotificationService.create_notification(
                        recipient_id=recipient.id,
                        sender_id=message.sender.id,
                        notification_type='message',
                        title=title,
                        body=body[:100],  # Max 100 characters
                        data=data
                    )
                    
                    if notification:
                        print(f"✅ Notification created with ID: {notification.id}")
                        serializer = NotificationSerializer(notification)
                        NotificationService.send_realtime_notification(
                            recipient.id,
                            serializer.data
                        )
                        print(f"✅ Realtime notification sent to {recipient.username}")
                    else:
                        print("🔴 Failed to create notification")
                        
                except Exception as e:
                    print(f"🔴 Error in private chat notification: {e}")
                    import traceback
                    traceback.print_exc()
            
            # ================ چت گروهی ================
            else:
                print(f"\n{'▶️'*10} GROUP CHAT NOTIFICATION {'◀️'*10}")
                try:
                    # Get all members except sender
                    members = chat_room.members.exclude(user_id=message.sender.id)
                    sender_name = message.sender.username
                    
                    # Get group name
                    try:
                        group_name = chat_room.group_info.group_name
                    except:
                        group_name = "گروه"
                    
                    print(f"👥 Group: {group_name}")
                    print(f"📊 Members count: {members.count()}")
                    
                    # ================ آماده‌سازی متن نوتیفیکیشن بر اساس نوع پیام ================
                    emoji_map = {
                        'text': '💬',
                        'image': '📷',
                        'audio': '🎤',
                        'video': '🎬',
                        'document': '📄',
                        'archive': '📦',
                        'file': '📎'
                    }
                    
                    type_map = {
                        'text': 'پیام',
                        'image': 'تصویر',
                        'audio': 'صدا',
                        'video': 'ویدیو',
                        'document': 'سند',
                        'archive': 'فایل فشرده',
                        'file': 'فایل'
                    }
                    
                    emoji = emoji_map.get(message.type_str, '📎')
                    persian_type = type_map.get(message.type_str, 'فایل')
                    
                    # عنوان نوتیفیکیشن
                    title = f"{emoji} {persian_type} جدید در {group_name}"
                    
                    # متن نوتیفیکیشن
                    if message.type_str == 'text':
                        body = f"{message.sender.username}: {message.content[:100]}" if message.content else f"پیام جدید از {message.sender.username}"
                    elif message.type_str == 'image':
                        body = f"{message.sender.username}: {emoji} تصویر {message.content or ''}"
                    elif message.type_str == 'audio':
                        body = f"{message.sender.username}: {emoji} پیام صوتی"
                    elif message.type_str == 'video':
                        body = f"{message.sender.username}: {emoji} ویدیو {message.content or ''}"
                    elif message.type_str == 'document':
                        body = f"{message.sender.username}: {emoji} سند {message.content or ''}"
                    else:
                        body = f"{message.sender.username}: {emoji} فایل {message.content or ''}"
                    
                    # اطلاعات پایه برای دیتا
                    base_data = {
                        'chat_id': chat_room.chat_id,
                        'chat_type': 'group',
                        'chat_name': group_name,
                        'message_id': message.msg_id,
                        'sender_id': message.sender.id,
                        'sender_name': message.sender.username,
                        'sender_username': message.sender.username,
                        'content': message.content[:50] if message.content else None,
                        'message_type': message.type_str,
                        'timestamp': str(message.timestamp),
                        'is_group': True
                    }
                    
                    # اضافه کردن URL فایل اگر وجود دارد
                    try:
                        if message.attachments.exists():
                            attachment = message.attachments.first()
                            base_data['file_url'] = attachment.file.url
                            base_data['file_name'] = attachment.file.name.split('/')[-1]
                            base_data['file_size'] = attachment.file_size
                    except:
                        pass
                    
                    # ارسال نوتیفیکیشن به هر عضو
                    notification_count = 0
                    for member in members:
                        # Skip excluded user
                        if exclude_user_id and member.user_id == exclude_user_id:
                            continue
                        
                        # Skip muted users
                        if member.is_muted:
                            print(f"🔇 User {member.user.username} is muted, skipping")
                            continue
                        
                        print(f"📨 Sending notification to {member.user.username} (ID: {member.user_id})")
                        
                        # Create notification for this member
                        notification = NotificationService.create_notification(
                            recipient_id=member.user_id,
                            sender_id=message.sender.id,
                            notification_type='message',
                            title=title,
                            body=body[:100],
                            data=base_data.copy()  
                        )
                        
                        if notification:
                            notification_count += 1
                            print(f"✅ Notification created for {member.user.username}")
                            serializer = NotificationSerializer(notification)
                            NotificationService.send_realtime_notification(
                                member.user_id,
                                serializer.data
                            )
                        else:
                            print(f"🔴 Failed to create notification for {member.user.username}")
                    
                    print(f"✅ Sent {notification_count} notifications to group members")
                            
                except Exception as e:
                    print(f"🔴 Error in group chat notification: {e}")
                    import traceback
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"🔴 Error in notify_new_message: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print(f"{'='*60}\n")

    @staticmethod
    def notify_group_invite(group_chat, invited_user, invited_by):
        
        notification = NotificationService.create_notification(
            recipient_id=invited_user.id,
            sender_id=invited_by.id,
            notification_type='group_invite',
            title=f"دعوت به گروه {group_chat.group_name}",
            body=f"{invited_by.username} شما را به گروه دعوت کرد",
            data={
                'chat_id': group_chat.chat.chat_id,
                'group_id': group_chat.chat.chat_id,
                'group_name': group_chat.group_name,
                'invited_by_id': invited_by.id,
                'invited_by_name': invited_by.username
            }
        )
        
        from .serializers import NotificationSerializer
        NotificationService.send_realtime_notification(
            invited_user.id,
            NotificationSerializer(notification).data
        )
    
    @staticmethod
    def notify_mention(message, chat_room, mentioned_users):
        """
        منشن شدن در پیام
        """
        for user in mentioned_users:
            notification = NotificationService.create_notification(
                recipient_id=user.id,
                sender_id=message.sender.id,
                notification_type='mention',
                title=f"منشن در {chat_room.group_info.group_name if chat_room.chat_type == 'group' else 'چت'}",
                body=f"{message.sender.username}: {message.content[:100]}",
                data={
                    'chat_id': chat_room.chat_id,
                    'message_id': message.msg_id,
                    'sender_id': message.sender.id
                }
            )
            
            from .serializers import NotificationSerializer
            NotificationService.send_realtime_notification(
                user.id,
                NotificationSerializer(notification).data
            )
    
    @staticmethod
    def notify_group_admin_promotion(group_chat, new_admin, promoted_by):
        """
        ارتقا به ادمین گروه
        """
        notification = NotificationService.create_notification(
            recipient_id=new_admin.id,
            sender_id=promoted_by.id,
            notification_type='group_admin',
            title=f"ادمین گروه {group_chat.group_name} شدید",
            body=f"شما توسط {promoted_by.username} به ادمین گروه ارتقا یافتید",
            data={
                'chat_id': group_chat.chat.chat_id,
                'group_name': group_chat.group_name
            }
        )
        
        from .serializers import NotificationSerializer
        NotificationService.send_realtime_notification(
            new_admin.id,
            NotificationSerializer(notification).data
        )
    
    @staticmethod
    def notify_removed_from_group(group_chat, removed_user, removed_by):
        """
        حذف از گروه
        """
        notification = NotificationService.create_notification(
            recipient_id=removed_user.id,
            sender_id=removed_by.id,
            notification_type='group_removed',
            title=f"از گروه {group_chat.group_name} حذف شدید",
            body=f"شما توسط {removed_by.username} از گروه حذف شدید",
            data={
                'chat_id': group_chat.chat.chat_id,
                'group_name': group_chat.group_name,
                'removed_by_id': removed_by.id
            }
        )
        
        from .serializers import NotificationSerializer
        NotificationService.send_realtime_notification(
            removed_user.id,
            NotificationSerializer(notification).data
        )