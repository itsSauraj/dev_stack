from django.contrib import admin
from django.urls import path, include
from users.views import Channel

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('projects.urls')),
    path("chat/", Channel.chat_view, name="chat-home"),
    path("chat/<uuid:profile_id>", Channel.chat, name="chat"),
    path("user/", include('users.urls')),
]
