from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from PIL import Image 
from io import BytesIO  
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Post, Hashtag, Comment
from socialapp.users.models import Notification
from .serializers import PostSerializer, HashtagSerializer, CommentSerializer
from .forms import PostForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_feed_api(request):
    # Get posts from users that the current user follows
    following_users = request.user.profile.following.values_list('user', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).order_by('-created_at')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

def home(request):
    """Home page view"""
    return render(request, 'posts/home.html')

@login_required
def news_feed(request):
    """News feed view"""
    form = PostForm()
    posts = Post.objects.select_related('author').prefetch_related('likes', 'comments').all()
    trending_hashtags = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    context = {
        'form': form,
        'posts': posts,
        'trending_hashtags': trending_hashtags,
    }
    return render(request, 'posts/news_feed.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        return Response({'liked': False})
    else:
        post.likes.add(request.user)
        return Response({'liked': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_share(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user != post.author:
        post.shares.add(request.user)
        return Response({'message': 'Post shared'})
    return Response(
        {'message': 'Cannot share your own post'},
        status=status.HTTP_400_BAD_REQUEST
    )

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            if 'image' in request.FILES:
                image = request.FILES['image']
                try:
                    # Process image with Pillow
                    img = Image.open(image)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Generate unique filename
                    import uuid
                    file_extension = image.name.split('.')[-1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    
                    # Save directly using ImageField
                    post.image.save(
                        unique_filename,
                        image,
                        save=False
                    )
                except Exception as e:
                    print(f"Image upload error: {str(e)}")  # Debug output
                    messages.error(request, 'Error uploading image')
                    return redirect('posts:news-feed')
            
            post.save()
            messages.success(request, 'Post created successfully!')
            
    return redirect('posts:news-feed')

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    if post.author != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def posts_by_hashtag(request, hashtag_name):
    hashtag = get_object_or_404(Hashtag, name=hashtag_name.lower())
    posts = Post.objects.filter(hashtags=hashtag)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comment_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'GET':
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            # Create notification
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                post=post
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        return Response({'message': 'Comment unliked'})
    else:
        comment.likes.add(request.user)
        # Create notification
        Notification.objects.create(
            recipient=comment.author,
            sender=request.user,
            notification_type='like',
            comment=comment
        )
        return Response({'message': 'Comment liked'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list(request):
    """API endpoint for posts list"""
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': liked
    })

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
    return redirect(request.META.get('HTTP_REFERER', reverse('posts:news-feed')))