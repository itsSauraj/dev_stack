from django.contrib import admin
from django.urls import path, include
from users.views import chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('projects.urls')),
    path("chat/<str:channel_id>", chat, name="chat"),
    path("user/", include('users.urls')),
]
