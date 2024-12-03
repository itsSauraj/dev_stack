import django_filters
from django.db.models import Q

from projects.models import Project
from users.models import Profile

class ProjectFilter(django_filters.FilterSet):
  
    creator__id = django_filters.UUIDFilter(field_name='creator__id')
  
    class Meta:
        model = Project
        fields = {
          'creator__id': ['exact'],
        }
        
        
class ProjectSearchFilter(django_filters.FilterSet):
  
    search = django_filters.CharFilter(method='search_query' , label='Search')
  
    class Meta:
        model = Project
        fields = ['search']
        
    def search_query(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(creator__name__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()