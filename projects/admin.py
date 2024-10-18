from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .models import Project, Tag

# Register your models here.
admin.site.register(Project)
admin.site.register(Tag)

# Administration Register your models here.
admin.site.register(LogEntry)