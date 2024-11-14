from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Review
from users.views import Profile
from .serializers import ReviewSerializer, PostReviewSerializer
from datetime import datetime, timezone

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class ReviewListView:
    
    @staticmethod
    @api_view(['GET', 'POST'])
    def get_post(request, project_id, *args, **kwargs):
        
        base_static_url = "http://" + request.get_host() + "/static"
        
        if request.method == 'GET':
            reviews_queryset = Review.objects.filter(project_id=project_id)
            paginator = Paginator(reviews_queryset, 8)
            
            page_number = request.GET.get('page')
            reviews_queryset = paginator.get_page(page_number)
            
            serializer = ReviewSerializer(reviews_queryset, many=True)
            
            total_rating = sum([review.get_review_stars() for review in reviews_queryset])
            average_rating = total_rating / len(reviews_queryset) if reviews_queryset else 0

            valid_data = serializer.data
            
            for data in valid_data:
                created_at_date = datetime.strptime(data.get('created_at'), '%Y-%m-%dT%H:%M:%S.%fZ')
                created_at_date = created_at_date.replace(tzinfo=timezone.utc)
                days_since_created = (datetime.now(timezone.utc) - created_at_date).days
                data['days_since_created'] = f"{days_since_created} days ago"
                
                if data.get('created_by') is not None:
                    creator = Profile.objects.get(id=data.get('created_by'))
                    data['created_by_name'] = creator.user.username if creator else 'Anonymous'
                    data['creator_avatar'] = base_static_url + creator.avatar.url
                else:
                    data['creator_avatar'] = base_static_url + "/images/avatars/default.png"
                    data['created_by_name'] = 'Anonymous'
                    
            context = {
                "reviews": valid_data,
                "total_reviews": len(valid_data),
                "average_rating": average_rating,
            }
            return Response(context, status=status.HTTP_200_OK)

        if request.method == 'POST':
            print(request.data)
            
            request.data["project"] = project_id
            
            if request.user.is_authenticated:
                request.data["created_by"] = request.user.profile.id or None
            
            serializer = PostReviewSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                
                data = serializer.data
                data['days_since_created'] = "Just now"
                
                if request.user.is_authenticated:
                    data['created_by_name'] = request.user.username or 'Anonymous'
                    data['creator_avatar'] = base_static_url + request.user.profile.avatar.url
                else:
                    data['creator_avatar'] = base_static_url + "/images/avatars/default.png"
                    data['created_by_name'] = 'Anonymous'
                
                return Response(data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)