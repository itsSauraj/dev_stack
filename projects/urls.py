from collections import namedtuple

from django.urls import path, include

from .views import ProjectsView, homepage
from .api_views import ReviewListView
from users.views import Channel


urlpatterns = [
    path('', homepage, name="home"),
    path("projects/", ProjectsView.projects, name="projects"),
    path("project/<str:pk>", ProjectsView.project, name="project"),
    path("create_project/", ProjectsView.create_project, name="create-project"),
    path("update_project/<str:pk>", ProjectsView.update_project, name="update-project"),
    path("delete_project/<str:pk>", ProjectsView.delete_project, name="delete-project"),
    
    
    # Chat URLS
    path("chat/", Channel.chat_view, name="chat-home"),
    path("chat/<uuid:chat_id>", Channel.chat, name="chat"),
    
    # API URLS using DRF
    path("api/reviews/<uuid:project_id>", ReviewListView.get_post, name="get-project-reviews"),
]
