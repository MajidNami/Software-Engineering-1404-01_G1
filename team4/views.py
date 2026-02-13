from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required

from django.conf import settings

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import ChatRoom, PrivateChat, Message , GroupChat , ChatParticipant , BlockList, UserReport
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


from .serializers import ChatRoomSerializer, MessageSerializer, UserBasicSerializer

TEAM_NAME = "team4"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

User = get_user_model()

# 1. Search Users to start a conversation (Now using Serializer for cleaner output)
# class UserSearchAPIView(generics.ListAPIView):
#     serializer_class = UserBasicSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         query = self.request.query_params.get('search', '')
#         # Finds users by username, excluding yourself
#         return User.objects.filter(
#             username__icontains=query
#         ).exclude(id=self.request.user.id)


class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserBasicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('search', '')   
        user = self.request.user
        
        # 1. Users I have blocked 
        blocked_by_me = BlockList.objects.filter(blocker=user).values_list('blocked_id', flat=True)
        # 2. Users who have blocked me
        blocking_me = BlockList.objects.filter(blocked=user).values_list('blocker_id', flat=True)
        
        # Combine them into a "hidden list"
        hidden_ids = list(blocked_by_me) + list(blocking_me)
        hidden_ids.append(user.id) # Exclude myself

        return User.objects.filter(
            username__icontains=query
        ).exclude(id__in=hidden_ids)


# 2. START A CHAT: Get an existing Private Chat ID or create a new one automatically
class StartPrivateChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('user_id')
        if not target_user_id: 
            return Response({"error": "Target user_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user1 = request.user
        try:
            user2 = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # CHECK: Does a private chat already exist between these two users?
        existing_chat = PrivateChat.objects.filter(
            (Q(user1=user1) & Q(user2=user2)) | 
            (Q(user1=user2) & Q(user2=user1))
        ).first()

        if existing_chat:
            return Response({"chat_id": existing_chat.chat_id, "new": False})

        # CREATE: If not, create a new ChatRoom entry first...
        new_room = ChatRoom.objects.create(chat_type='private')
        # ...then create the PrivateChat entry linked to it
        PrivateChat.objects.create(chat=new_room, user1=user1, user2=user2)
        
        return Response({"chat_id": new_room.chat_id, "new": True}, status=status.HTTP_201_CREATED)


# 3. GET INBOX: All chats I'm participating in
class MyChatRoomsView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Find ChatRooms where User is user1, user2 (private) OR a participant (group)
        return ChatRoom.objects.filter(
            Q(private_info__user1=user) | 
            Q(private_info__user2=user) | 
            Q(members__user=user)
        ).distinct().order_by('-updated_at')


# 4. GET HISTORY: Get all messages for a specific room
class ChatHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id).order_by('timestamp')

# Add this near other imports at the top
from django.shortcuts import get_object_or_404

# ... (Previous Search and History views) ...

class CreateGroupChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        name = request.data.get('group_name')
        user_ids = request.data.get('user_ids', [])
        if not name: return Response({"error": "Group name is required"}, status=400)
        new_room = ChatRoom.objects.create(chat_type='group')
        GroupChat.objects.create(chat=new_room, group_name=name, admin=request.user)
        ChatParticipant.objects.create(user=request.user, chat=new_room, is_admin=True)
        for uid in user_ids:
            try:
                target_user = User.objects.get(id=uid)
                if target_user != request.user:
                    ChatParticipant.objects.create(user=target_user, chat=new_room)
            except User.DoesNotExist: continue
        return Response({"chat_id": new_room.chat_id, "message": "Group created successfully"}, status=201)

class AddMemberToGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, chat_id):
        is_admin = ChatParticipant.objects.filter(user=request.user, chat_id=chat_id, is_admin=True).exists()
        if not is_admin: return Response({"error": "Admin required"}, status=403)
        user_id_to_add = request.data.get('user_id')
        user_to_add = get_object_or_404(User, id=user_id_to_add)
        ChatParticipant.objects.get_or_create(user=user_to_add, chat_id=chat_id)
        return Response({"message": f"{user_to_add.username} added."})


import os
from rest_framework.parsers import MultiPartParser, FormParser

class AttachmentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # Necessary for file uploads

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Physical storage handling (Django automatically creates /media/attachments/)
        from django.core.files.storage import default_storage
        file_path = f"attachments/{file_obj.name}"
        saved_path = default_storage.save(file_path, file_obj)
        
        # 2. Get file metadata for your ERD fields
        file_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        file_type = file_obj.content_type # e.g. "image/png"
        file_size = file_obj.size / 1024 # Store in KB

        # Note: We don't link it to a message yet! 
        # We just return the details so the user can "send" it in a message.
        return Response({
            "file_url": file_url,
            "file_type": file_type,
            "file_size": file_size,
            "file_name": file_obj.name
        }, status=status.HTTP_201_CREATED)



class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, msg_id):
        # Only the sender can delete their own message
        message = get_object_or_404(Message, msg_id=msg_id, sender=request.user)
        
        message.is_deleted = True
        message.content = "This message was deleted" # Optional: hide content
        message.save()

        return Response({"message": "Message marked as deleted"})


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List everyone I have blocked"""
        blocked_users = BlockList.objects.filter(blocker=request.user)
        data = UserBasicSerializer([b.blocked for b in blocked_users], many=True).data
        return Response(data)

    def post(self, request):
        """Block a user"""
        target_id = request.data.get('user_id')
        if not target_id: return Response({"error": "user_id required"}, 400)
        
        target_user = get_object_or_404(User, id=target_id)
        if target_user == request.user:
            return Response({"error": "You cannot block yourself"}, 400)

        BlockList.objects.get_or_create(blocker=request.user, blocked=target_user)
        return Response({"message": f"Blocked {target_user.username}"})

    def delete(self, request):
        """Unblock a user"""
        target_id = request.data.get('user_id')
        BlockList.objects.filter(blocker=request.user, blocked_id=target_id).delete()
        return Response({"message": "User unblocked"})

# 2. Reporting Logic
class ReportUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_id = request.data.get('user_id')
        reason = request.data.get('reason')
        
        if not target_id or not reason:
            return Response({"error": "user_id and reason required"}, 400)

        reported_user = get_object_or_404(User, id=target_id)
        
        UserReport.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            reason=reason
        )
        return Response({"message": "Report submitted. Our team will review it."})
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token_view(request):
    return Response({"message": f"Successfully authenticated as {request.user.username}"})


User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny] # Anyone can register

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error': 'Please provide all fields'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Generate tokens so they are logged in immediately after registering
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'username': user.username,
                'email': user.email
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)