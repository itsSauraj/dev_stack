from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile

    
@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):    
    if created:
        Profile.objects.create(
          user = instance, 
          name = instance.first_name + " " + instance.last_name
        )
    instance.profile.save()
    
@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):    
    try:
      projects = instance.profile.project_set.all()
      skills = instance.profile.skill_set.all()
      for project in projects:
        project.delete()
      for skill in skills:
        skill.delete()
      instance.profile.delete()
    except:
      pass
    
@receiver(post_save, sender=Profile)
def profile_updated(sender, instance, **kwargs):    
    name = instance.name
    
    try:
      first_name = name.split(" ")[0] or ""
    except:
      first_name = name
    try:
      last_name = name.split(" ")[1] or ""
    except:
      last_name = ""
    
    User.objects.filter(profile=instance).update(first_name=first_name, last_name=last_name)
        