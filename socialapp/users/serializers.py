from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Notification  
from socialapp.posts.models import Post, Comment 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'bio', 'profile_picture', 'followers_count', 
                 'following_count', 'created_at', 'updated_at')


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    post_id = serializers.ReadOnlyField(source='post.id', allow_null=True)
    comment_id = serializers.ReadOnlyField(source='comment.id', allow_null=True)

    class Meta:
        model = Notification
        fields = ('id', 'sender_username', 'notification_type', 
                 'post_id', 'comment_id', 'created_at', 'is_read')
        read_only_fields = ('created_at',)