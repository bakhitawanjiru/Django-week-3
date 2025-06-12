from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),
    path('<int:post_id>/like/', views.post_like, name='post-like'),
    path('<int:post_id>/comments/', views.post_comments, name='post-comments'),
]