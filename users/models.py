import uuid
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        
class User(AbstractUser, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    socket_id = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return str(self.username)

    @property
    def online_status(self):
        return self.is_online
    
class Skills(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    level = models.IntegerField(default=1)
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    bg_color = models.CharField(max_length=7, default="#007bff")
    fg_color = models.CharField(max_length=7, default="#ffffff")
    
    def __str__(self):
        return str(self.name)

      
class Profile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255)
    short_intro = models.TextField(null=True, blank=True)
    short_bio = models.TextField(null=True, blank=True)
    social_github = models.CharField(max_length=200, blank=True, null=True)
    social_twitter = models.CharField(max_length=200, blank=True, null=True)
    social_linkedin = models.CharField(max_length=200, blank=True, null=True)
    social_youtube = models.CharField(max_length=200, blank=True, null=True)
    social_website = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{str(self.name)} - {str(self.user.username)}"
    
    @property
    def skill_set(self):
        return Skills.objects.filter(profile=self.user)
    
    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return "avatars/default.png"

class ChatRecords(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_members = models.ManyToManyField(User)
    
    def __str__(self):
        return f"{self.id}"
    
    @classmethod
    def get_user_chats(cls, user):
        return cls.objects.filter(chat_members=user)
    
    @classmethod
    def get_user_chats(cls, user, chat_id):
        return cls.objects.filter(chat_members=user, chat_id=chat_id)
    
    @classmethod
    def create_chat_record(cls, members):
        chat_record = cls.objects.create()
        for member in members:
            chat_record.chat_members.add(member)
        return chat_record

class Message(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_id = models.ForeignKey(ChatRecords, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    sent_at = models.DateTimeField(default=None, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username} - {self.message[:20]}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
        
    def mark_as_sent(self):
        self.is_sent = True
        self.save()
