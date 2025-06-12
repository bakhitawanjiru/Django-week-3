from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.news_feed, name='news-feed'),
    path('create/', views.create_post, name='create-post'),
    path('api/posts/', views.post_list, name='post-list'),
    path('api/posts/<int:post_id>/', views.post_detail, name='post-detail'),
    path('api/posts/<int:post_id>/like/', views.post_like, name='post-like'),
    path('post/<int:post_id>/like/', views.like_post, name='like-post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add-comment'),
]