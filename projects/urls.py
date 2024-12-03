from collections import namedtuple

from django.urls import path, include

from . import views
from .api_views import ReviewListView
from users.views import Channel


urlpatterns = [
    path('', views.homepage, name="home"),
    path("projects/", views.projects, name="projects"),
    path("project/<str:pk>", views.project, name="project"),
    path("create_project/", views.create_project, name="create-project"),
    path("update_project/<str:pk>", views.update_project, name="update-project"),
    path("delete_project", views.delete_project, name="delete-project"),
    path("delete_project/<str:pk>", views.delete_project, name="delete-project"),
    
    
    # Chat URLS
    path("chat/", Channel.chat_view, name="chat-home"),
    path("chat/<uuid:chat_id>", Channel.chat, name="chat"),
    
    # API URLS using DRF
    path("api/reviews/<uuid:project_id>", ReviewListView.get_post, name="get-project-reviews"),
]
