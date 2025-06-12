from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),  # Move this before the username pattern
    path('profile/', views.profile, name='profile'),  # Own profile
    path('profile/<str:username>/', views.profile, name='profile-detail'),  # Other user's profile
]