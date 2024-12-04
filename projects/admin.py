from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .models import Project, Tag, Review


from django_summernote.admin import SummernoteModelAdmin

admin.site.register(Review)
admin.site.register(Tag)

# Administration Register your models here.
admin.site.register(LogEntry)

class ProjectAdmin(SummernoteModelAdmin):
    summernote_fields = 'description'
    
admin.site.register(Project, ProjectAdmin)