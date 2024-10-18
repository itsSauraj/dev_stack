from collections import namedtuple

from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.homepage, name="home"),
    path("projects/", views.projects, name="projects"),
    path("project/<str:pk>", views.project, name="project"),
    path("create_project/", views.create_project, name="create-project"),
    path("update_project/<str:pk>", views.update_project, name="update-project"),
    path("delete_project", views.delete_project, name="delete-project"),
    path("delete_project/<str:pk>", views.delete_project, name="delete-project"),
]
