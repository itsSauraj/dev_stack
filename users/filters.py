import django_filters
from django.db.models import Q

from projects.models import Project
from users.models import Profile

class ProfileFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_query', label='Search')

    class Meta:
        model = Profile
        fields = ['search']

    def search_query(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(short_intro__icontains=value) |
            Q(short_bio__icontains=value) | 
            Q(user__skills__name__icontains=value)
        ).distinct()