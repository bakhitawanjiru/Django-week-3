from rest_framework import serializers
from .models import Post, Hashtag, Comment

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'name')

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    like_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    hashtags = HashtagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'author_username', 'content', 'image',
                 'video', 'hashtags', 'created_at', 'updated_at', 'like_count', 'share_count',
                 'is_liked')
        read_only_fields = ('author', 'hashtags', 'created_at', 'updated_at')

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        post.extract_hashtags()
        return post

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.hashtags.clear()
        instance.extract_hashtags()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'author_username', 'content',
                 'created_at', 'updated_at', 'like_count', 'is_liked')
        read_only_fields = ('author', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()