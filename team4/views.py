from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import ChatRoom, PrivateChat, GroupChat, ChatParticipant, Message, Attachment 
from .serializers import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.services import NotificationService

TEAM_NAME = "team4"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")



User = get_user_model()

class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.query_params.get('search', '')
        users = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id)
        return Response(UserBasicSerializer(users, many=True, context={'request': request}).data)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBasicSerializer
    def get_object(self): return self.request.user

class MyChatRoomsView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(private_info__user1=user)|Q(private_info__user2=user)|Q(members__user=user)).distinct().order_by('-updated_at')

class ChatHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Message.objects.filter(chat_id=self.kwargs['chat_id']).order_by('timestamp')

class FileUploadView(APIView):
   
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, chat_id):
        print(f"\n{'='*60}")
        print(f"📁 FILE UPLOAD REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"👤 User: {request.user.username} (ID: {request.user.id})")
        print(f"💬 Chat ID: {chat_id}")
        print(f"📦 FILES in request: {dict(request.FILES)}")
        print(f"📝 DATA in request: {dict(request.data)}")
        print(f"{'='*60}\n")

        # ================ 1. بررسی وجود فایل ================
        if 'file' not in request.FILES:
            print("❌ No file in request.FILES")
            print(f"Available keys: {list(request.FILES.keys())}")
            return Response(
                {"error": "فایلی ارسال نشده است. کلید 'file' در درخواست وجود ندارد."}, 
                status=400
            )
        
        file_obj = request.FILES['file']
        print(f"📄 File received:")
        print(f"  - Name: {file_obj.name}")
        print(f"  - Size: {file_obj.size} bytes")
        print(f"  - Type: {file_obj.content_type}")

        # ================ 2. بررسی حجم فایل ================
        max_size = 50 * 1024 * 1024  # 50MB
        if file_obj.size > max_size:
            print(f"❌ File too large: {file_obj.size} > {max_size}")
            return Response(
                {"error": f"حجم فایل نباید بیشتر از 50 مگابایت باشد. حجم فایل شما: {file_obj.size / 1024 / 1024:.1f}MB"}, 
                status=400
            )

        # ================ 3. تشخیص نوع فایل ================
        file_name = file_obj.name.lower()
        file_type = self._detect_file_type(file_name, file_obj.content_type)
        print(f"📁 Detected file type: {file_type}")

        # ================ 4. دریافت چت ================
        try:
            room = ChatRoom.objects.get(chat_id=chat_id)
            print(f"✅ Chat room found: {room.chat_id} ({room.chat_type})")
        except ChatRoom.DoesNotExist:
            print(f"❌ Chat room not found with ID: {chat_id}")
            return Response(
                {"error": f"چت با شناسه {chat_id} یافت نشد"}, 
                status=404
            )

        # ================ 5. بررسی عضویت ================
        is_member = ChatParticipant.objects.filter(
            chat=room, 
            user=request.user
        ).exists()
        
        if not is_member:
            print(f"❌ User {request.user.username} is not a member of chat {chat_id}")
            return Response(
                {"error": "شما عضو این چت نیستید"}, 
                status=403
            )
        print(f"✅ User is member of chat")

        # ================ 6. بررسی Mute برای گروه ================
        if room.chat_type == 'group':
            participant = ChatParticipant.objects.filter(
                chat=room, 
                user=request.user
            ).first()
            
            if participant and participant.is_muted:
                print(f"🔇 User is muted in this group")
                return Response(
                    {"error": "شما در این گروه بیصدا هستید"}, 
                    status=403
                )

        # ================ 7. ذخیره پیام و فایل ================
        try:
            # محتوای پیام (caption یا نام فایل)
            content_text = request.data.get('caption', file_obj.name)
            print(f"📝 Message content: {content_text}")

            # ایجاد پیام
            msg = Message.objects.create(
                sender=request.user,
                chat=room,
                content=content_text,
                type_str=file_type
            )
            print(f"✅ Message created with ID: {msg.msg_id}")

            # ایجاد Attachment
            try:
                att = Attachment.objects.create(
                    message=msg, 
                    file=file_obj,
                    file_type=file_type,
                    file_size=file_obj.size
                )
                print(f"✅ Attachment created with ID: {att.file_id}")
                print(f"📎 File saved at: {att.file.url}")
                print(f"📎 Full path: {att.file.path}")
            except Exception as e:
                print(f"❌ Error creating attachment: {e}")
                
                msg.delete()
                raise e

            # ================ 8. ساخت URL کامل ================
            try:
                file_full_url = request.build_absolute_uri(att.file.url)
                print(f"🔗 File URL: {file_full_url}")
            except Exception as e:
                print(f"⚠️ Error building absolute URI: {e}")
                file_full_url = att.file.url

            # ================ 9. ارسال به WebSocket ================
            message_data = {
                'type': 'chat_message',
                'message': msg.content,
                'file_url': file_full_url,
                'type_str': file_type,
                'msg_id': msg.msg_id,
                'sender_username': request.user.username,
                'sender_id': request.user.id,
                'timestamp': str(msg.timestamp),
                'is_edited': False,
                'file_name': file_obj.name,
                'file_size': file_obj.size
            }

            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'chat_{chat_id}',
                    message_data
                )
                print(f"✅ WebSocket message sent to group chat_{chat_id}")
            except Exception as e:
                print(f"⚠️ Error sending WebSocket message: {e}")
                

            # ================ 10. ارسال نوتیفیکیشن ================
            try:
                from users.services import NotificationService
                NotificationService.notify_new_message(msg, room, request.user.id)
                print(f"✅ Notification sent")
            except Exception as e:
                print(f"⚠️ Error sending notification: {e}")
                

            # ================ 11. پاسخ ================
            response_data = AttachmentSerializer(
                att, 
                context={'request': request}
            ).data
            response_data['message_id'] = msg.msg_id
            response_data['file_url'] = file_full_url
            
            print(f"\n✅✅✅ FILE UPLOAD COMPLETED SUCCESSFULLY ✅✅✅")
            print(f"{'='*60}\n")
            
            return Response(response_data, status=201)
            
        except Exception as e:
            print(f"\n❌❌❌ ERROR IN FILE UPLOAD ❌❌❌")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            return Response(
                {"error": f"خطا در آپلود فایل: {str(e)}"}, 
                status=500
            )

    def _detect_file_type(self, file_name, content_type):
        
        # تصاویر
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        if any(file_name.endswith(ext) for ext in image_extensions):
            return 'image'
        
        # صدا/ویس
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.aac', '.flac']
        if any(file_name.endswith(ext) for ext in audio_extensions):
            return 'audio'
        
        # ویدیو
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        if any(file_name.endswith(ext) for ext in video_extensions):
            return 'video'
        
        # سند
        document_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.txt', '.rtf', '.odt'
        ]
        if any(file_name.endswith(ext) for ext in document_extensions):
            return 'document'
        
        # فایل فشرده
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
        if any(file_name.endswith(ext) for ext in archive_extensions):
            return 'archive'
        
        # سایر
        return 'file'
    
class GetOrCreatePrivateChat(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, target_user_id):
        target_user = get_object_or_404(User, id=target_user_id)
        user = request.user
        
        
        if user.id == target_user.id:
            return Response({"error": "Cannot chat with yourself"}, status=400)
        
        # Check if chat already exists
        existing = ChatRoom.objects.filter(
            chat_type='private',
            private_info__user1__in=[user, target_user],
            private_info__user2__in=[user, target_user]
        ).first()
        
        if existing:
           
            if not ChatParticipant.objects.filter(chat=existing, user=user).exists():
                ChatParticipant.objects.create(chat=existing, user=user)
                print(f"✅ Added missing participant {user.username} to chat {existing.chat_id}")
            
            if not ChatParticipant.objects.filter(chat=existing, user=target_user).exists():
                ChatParticipant.objects.create(chat=existing, user=target_user)
                print(f"✅ Added missing participant {target_user.username} to chat {existing.chat_id}")
            
            serializer = ChatRoomSerializer(existing, context={'request': request})
            return Response(serializer.data)
        
        # Create new private chat
        print(f"🆕 Creating new private chat between {user.username} and {target_user.username}")
        new_room = ChatRoom.objects.create(chat_type='private')
        PrivateChat.objects.create(chat=new_room, user1=user, user2=target_user)
        
        
        ChatParticipant.objects.create(chat=new_room, user=user)
        ChatParticipant.objects.create(chat=new_room, user=target_user)
        print(f"✅ Participants added: {user.username} and {target_user.username}")
        
        serializer = ChatRoomSerializer(new_room, context={'request': request})
        
        # Send real-time update to both users
        try:
            channel_layer = get_channel_layer()
            
            # Send to current user
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'chat_list_updated',
                    'chat': serializer.data
                }
            )
            
            # Send to target user
            async_to_sync(channel_layer.group_send)(
                f'notifications_{target_user.id}',
                {
                    'type': 'chat_list_updated',
                    'chat': serializer.data
                }
            )
            print(f"✅ Real-time update sent to both users")
        except Exception as e:
            print(f"⚠️ Error sending real-time update: {e}")
        
        return Response(serializer.data, status=201)

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('name')
        user_ids = request.data.get('users', [])
        room = ChatRoom.objects.create(chat_type='group')
        GroupChat.objects.create(chat=room, group_name=name, admin=request.user)
        ChatParticipant.objects.create(chat=room, user=request.user, is_admin=True)
        for u_id in user_ids:
            ChatParticipant.objects.create(chat=room, user_id=u_id)
        return Response(ChatRoomSerializer(room, context={'request': request}).data)

class GroupMembersListView(generics.ListAPIView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ChatParticipant.objects.filter(chat_id=self.kwargs['chat_id'])

class GroupMemberActionView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, chat_id):
        
        is_admin = ChatParticipant.objects.filter(
            chat_id=chat_id, 
            user=request.user, 
            is_admin=True
        ).exists()
        
        if not is_admin:
            return Response(
                {"error": "فقط ادمین گروه می‌تواند این عملیات را انجام دهد"}, 
                status=403
            )
        
        target_uid = request.data.get('user_id')
        action = request.data.get('action')
        
        if not target_uid or not action:
            return Response(
                {"error": "user_id and action are required"}, 
                status=400
            )
        
        try:
            
            participant = get_object_or_404(
                ChatParticipant, 
                chat_id=chat_id, 
                user_id=target_uid
            )
            
            # دریافت اطلاعات گروه برای نوتیفیکیشن
            group = get_object_or_404(GroupChat, chat_id=chat_id)
            target_user = get_object_or_404(User, id=target_uid)
            
            
            if action == 'promote':
                # ارتقا به ادمین
                participant.is_admin = True
                participant.save()
                
                # ارسال نوتیفیکیشن
                from users.services import NotificationService
                NotificationService.notify_group_admin_promotion(
                    group, 
                    target_user, 
                    request.user
                )
                
                return Response({
                    "msg": f"کاربر {target_user.username} به ادمین ارتقا یافت",
                    "is_admin": True
                })
                
            elif action == 'demote':
                
                if target_uid == request.user.id:
                    admin_count = ChatParticipant.objects.filter(
                        chat_id=chat_id, 
                        is_admin=True
                    ).count()
                    if admin_count <= 1:
                        return Response(
                            {"error": "شما تنها ادمین گروه هستید و نمی‌توانید خود را تنزل دهید"}, 
                            status=400
                        )
                
                participant.is_admin = False
                participant.save()
                
                return Response({
                    "msg": f"کاربر {target_user.username} از ادمینی تنزل یافت",
                    "is_admin": False
                })
                
            elif action == 'remove':
                if participant.is_admin and target_uid != request.user.id:
                    return Response(
                        {"error": "نمی‌توان ادمین را از گروه حذف کرد"}, 
                        status=400
                    )
                
                
                user_name = target_user.username
                
                # ارسال نوتیفیکیشن قبل از حذف
                from users.services import NotificationService
                NotificationService.notify_removed_from_group(
                    group, 
                    target_user, 
                    request.user
                )
                
                # حذف کاربر
                participant.delete()
                
                return Response({
                    "msg": f"کاربر {user_name} از گروه حذف شد"
                })
                
            elif action == 'mute':
                # بیصدا کردن
                participant.is_muted = True
                participant.save()
                
                return Response({
                    "msg": f"کاربر {target_user.username} بیصدا شد",
                    "is_muted": True
                })
                
            elif action == 'unmute':
                # برگرداندن صدا
                participant.is_muted = False
                participant.save()
                
                return Response({
                    "msg": f"صدای کاربر {target_user.username} برگردانده شد",
                    "is_muted": False
                })
                
            elif action == 'leave':
                # خروج از گروه (برای کاربر عادی)
                if target_uid != request.user.id:
                    return Response(
                        {"error": "شما فقط می‌توانید خودتان را از گروه خارج کنید"}, 
                        status=400
                    )
                
                
                if participant.is_admin:
                    admin_count = ChatParticipant.objects.filter(
                        chat_id=chat_id, 
                        is_admin=True
                    ).count()
                    
                    if admin_count <= 1:
                        
                        other_admin = ChatParticipant.objects.filter(
                            chat_id=chat_id
                        ).exclude(user_id=target_uid).first()
                        
                        if other_admin:
                            other_admin.is_admin = True
                            other_admin.save()
                        else:
                        
                            group.chat.delete()
                            return Response({"msg": "گروه حذف شد"})
                
                participant.delete()
                return Response({"msg": "شما از گروه خارج شدید"})
            
            else:
                return Response(
                    {"error": f"عملیات نامعتبر: {action}"}, 
                    status=400
                )
                
        except ChatParticipant.DoesNotExist:
            return Response(
                {"error": "کاربر مورد نظر در این گروه یافت نشد"}, 
                status=404
            )
        except Exception as e:
            return Response(
                {"error": f"خطا در انجام عملیات: {str(e)}"}, 
                status=500
            )

class GroupChatUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, chat_id):
        group = get_object_or_404(GroupChat, chat_id=chat_id)
        is_admin = ChatParticipant.objects.filter(chat=group.chat, user=request.user, is_admin=True).exists()
        return Response({'details': GroupChatSerializer(group, context={'request': request}).data, 'can_edit': is_admin})
    def patch(self, request, chat_id):
        group = get_object_or_404(GroupChat, chat_id=chat_id)
        if not ChatParticipant.objects.filter(chat=group.chat, user=request.user, is_admin=True).exists():
            return Response({"error": "عدم دسترسی"}, status=403)
        ser = GroupChatUpdateSerializer(group, data=request.data, partial=True)
        if ser.is_valid(): ser.save(); return Response(ser.data)
        return Response(ser.errors, status=400)

class ToggleMuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        # Find the participant entry for this user in this chat
        participant = get_object_or_404(ChatParticipant, chat_id=chat_id, user=request.user)
        
        # Toggle the status
        participant.is_muted = not participant.is_muted
        participant.save()
        
        return Response({'is_muted': participant.is_muted, 'msg': 'Mute status updated'})
    


class EditMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, msg_id):
        
        message = get_object_or_404(Message, msg_id=msg_id, sender=request.user)
        new_content = request.data.get('content')
        
        if not new_content:
            return Response({"error": "محتوا نمی‌تواند خالی باشد"}, status=400)
        
        message.content = new_content
        message.is_edited = True
        message.save()
        
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{message.chat.chat_id}',
            {
                'type': 'message_updated',
                'msg_id': message.msg_id,
                'new_content': message.content,
                'is_edited': True
            }
        )
        return Response({"message": "پیام ویرایش شد"})

class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, msg_id):
        
        message = get_object_or_404(Message, msg_id=msg_id, sender=request.user)
        chat_id = message.chat.chat_id
        msg_id_copy = message.msg_id
        
        message.delete()
        
        # ارسال خبر حذف به همه (Websocket)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chat_id}',
            {
                'type': 'message_deleted',
                'msg_id': msg_id_copy
            }
        )
        return Response({"message": "پیام حذف شد"})
    

from .models import User, Notification
from .serializers import (
    UserBasicSerializer, 
    NotificationSerializer, 
    WebPushSubscriptionSerializer
)



@api_view(['GET'])
@permission_classes([IsAuthenticated])

def test_token_view(request):
    return Response({"message": f"Successfully authenticated as {request.user.username}"})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error': 'Please provide all fields'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'username': user.username,
                'email': user.email
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


# ==================== Notification Views ====================

class NotificationListView(generics.ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        

        unread_seen = queryset.filter(is_read=False, is_seen=False)
        unread_seen.update(is_seen=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """جزئیات نوتیفیکیشن و مارک به عنوان خوانده شده"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class MarkAllNotificationsReadView(APIView):
    """مارک کردن همه نوتیفیکیشن‌ها به عنوان خوانده شده"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            'marked_read_count': count,
            'message': f'{count} notification marked as read'
        })


class UnreadNotificationCountView(APIView):
    """تعداد نوتیفیکیشن‌های خوانده نشده"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})


class DeleteAllNotificationsView(APIView):
    """حذف همه نوتیفیکیشن‌ها"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        Notification.objects.filter(recipient=request.user).delete()
        return Response({'message': 'All notifications deleted'}, status=status.HTTP_204_NO_CONTENT)



class RegisterWebPushSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = WebPushSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            request.user.web_push_subscription = serializer.validated_data['subscription']
            request.user.save()
            return Response({'message': 'Web Push subscription registered successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteNotificationView(APIView):
    """حذف یک نوتیفیکیشن خاص"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.delete()
        return Response({'message': 'Notification deleted'}, status=status.HTTP_204_NO_CONTENT)