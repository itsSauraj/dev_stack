from django.urls import path
import users.views


urlpatterns = [
  path("login/", users.views.login_user, name="login"),
  path("logout/", users.views.logout_user, name="logout"),
  path("register/", users.views.register_user, name="register"),
  path("delete/", users.views.delete_user, name="user-delete"),
  
  
  path("profile/", users.views.profile, name="profile"),
  path("profile/update", users.views.update_profile, name="update-profile"),
  path("profile/<str:pk>", users.views.view_profile, name="developer-view"),
  path("developers", users.views.get_developers, name="developers"),
  
  path("skills/<str:pk>", users.views.addSkill, name="add-skill"),
  path("skills/u/<str:pk>", users.views.updateSkill, name="update-skill"),
  path("skills/d/<str:pk>", users.views.deleteSkill, name="delete-skill"),
]