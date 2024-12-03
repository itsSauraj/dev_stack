from django.urls import path, re_path
from users import consumers

websocket_urlpatterns = [
    # path('ws/chat-server/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<group_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]