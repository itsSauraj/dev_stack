import uuid

from django.db import models

# Create your models here.
class BaseModal(models.Model):
    '''
    Base Model for all the other modals
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        abstract = True

class Project(BaseModal):
    '''
    Project Modal
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poster = models.ImageField(upload_to="posters/", default="posters/default.jpg")
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    demo_link = models.URLField(blank=True, null=True)
    source_link = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    creator = models.ForeignKey('users.Profile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title} - {self.creator.user.username}"
    
    @property
    def poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        else:
            return "images/posters/default.jpg"


class Tag(models.Model):
    name = models.CharField(max_length=200)
    creator = models.ForeignKey('users.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='tags')
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.name
    

class Review(BaseModal):
    '''
    Review Modal
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField(blank=True, null=True)
    value = models.IntegerField(range(1, 6), default=0, blank=True, null=True)
    created_by = models.ForeignKey('users.Profile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.value} - {self.body[:20]} | {self.created_by}"
    
    def get_review_stars(self):
        reviews = self.project.reviews.all()
        sum = 0
        for review in reviews:
            sum += review.value
        if len(reviews) > 0:
            return round(sum / len(reviews))
        return 0