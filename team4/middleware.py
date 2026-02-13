from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception as e:
        print(f"Middleware JWT Error: {e}")
        return AnonymousUser()      

class JWTAuthMiddleware:
    """
    Custom middleware that takes a token from the query string and authenticates a user
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope['query_string'].decode())
        token = query_params.get('token')

        if token:
            scope['user'] = await get_user(token[0])
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)