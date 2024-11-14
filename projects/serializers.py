from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'project', 'body', 'value', 'created_by', 'created_at']   
        read_only_fields = ('project', 'created_at', 'updated_at')

class PostReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"