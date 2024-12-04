from django.urls import path
from users.views import AuthenticationView, UserView


urlpatterns = [
  path("login/", AuthenticationView.login_user, name="login"),
  path("logout/", AuthenticationView.logout_user, name="logout"),
  path("register/", AuthenticationView.register_user, name="register"),
  path("delete/", UserView.delete_user, name="user-delete"),
  
  
  path("profile/", UserView.profile, name="profile"),
  path("profile/update", UserView.update_profile, name="update-profile"),
  path("profile/<str:pk>", UserView.view_profile, name="developer-view"),
  path("developers", UserView.get_developers, name="developers"),
  
  path("skills/<str:pk>", UserView.addSkill, name="add-skill"),
  path("skills/u/<str:pk>", UserView.updateSkill, name="update-skill"),
  path("skills/d/<str:pk>", UserView.deleteSkill, name="delete-skill"),
]