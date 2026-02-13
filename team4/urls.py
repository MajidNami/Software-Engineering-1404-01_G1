# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.base),
#     path("ping/", views.ping),
# ]


from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# from users.views import RegisterView
from views import RegisterView, test_token_view

from views import (
    UserSearchAPIView, 
    StartPrivateChatAPIView, 
    MyChatRoomsView, 
    ChatHistoryView
)

from views import (
    UserSearchAPIView, 
    StartPrivateChatAPIView, 
    MyChatRoomsView, 
    ChatHistoryView,
    CreateGroupChatView,   
    AddMemberToGroupView,   
    AttachmentUploadView
)

from django.conf import settings
from django.conf.urls.static import static
from views import BlockUserView, ReportUserView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Registration
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # Login: Send username & password, get Access and Refresh tokens
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refresh: Send Refresh token, get a new Access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/test-token/', test_token_view, name='test_token'),

    # path('api/search-users/', UserSearchView.as_view(), name='search_users'),
    # path('api/my-chats/', MyChatRoomsView.as_view(), name='my_chats'),
    # path('api/chat-history/<int:chat_id>/', ChatHistoryView.as_view(), name='chat_history'), 
    path('api/users/search/', UserSearchAPIView.as_view(), name='user_search'),
    path('api/chat/start/', StartPrivateChatAPIView.as_view(), name='start_chat'),
    path('api/chat/inbox/', MyChatRoomsView.as_view(), name='inbox'),
    path('api/chat/history/<int:chat_id>/', ChatHistoryView.as_view(), name='history'),
    path('api/chat/groups/create/', CreateGroupChatView.as_view(), name='create_group'),
    path('api/chat/groups/<int:chat_id>/add-member/', AddMemberToGroupView.as_view(), name='add_member'),
    path('api/chat/upload/', AttachmentUploadView.as_view()),
    path('api/safety/block/', BlockUserView.as_view(), name='block_user'),
    path('api/safety/report/', ReportUserView.as_view(), name='report_user'),

]



# Add this to the very bottom
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)