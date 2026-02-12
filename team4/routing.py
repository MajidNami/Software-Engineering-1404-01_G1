from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Pattern: ws://127.0.0.1:8000/ws/chat/<room_id>/
    re_path(r'ws/chat/(?P<room_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]