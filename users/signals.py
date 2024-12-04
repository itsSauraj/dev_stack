from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Profile, User
    
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
      
      #deleting user's projects
      for project in projects:
        project.delete()
        
      #deleting user's skills
      for skill in skills:
        skill.delete()
      
      #deleting user's chat records
      for chatRecords in instance.profile.chat_records.all():
        #deleting user's messages
        for message in chatRecords.message_set.all():
          message.delete()
        chatRecords.delete()
        
      #deleting user's reviews
      for review in instance.profile.review_set.all():
        review.delete()
      
      #deleting user's profile
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
        