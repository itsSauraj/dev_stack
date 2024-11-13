import django_filters

from .models import Project

class ProjectFilter(django_filters.FilterSet):
  
    creator__id = django_filters.UUIDFilter(field_name='creator__id')
  
    class Meta:
        model = Project
        fields = {
          'creator__id': ['exact'],
        }