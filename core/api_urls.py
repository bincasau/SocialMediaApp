from django.urls import path

from .api_views import (
    CommentListCreateAPIView,
    FollowToggleAPIView,
    HealthAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    MessageCollectionAPIView,
    MessageThreadAPIView,
    PostCollectionAPIView,
    PostDetailAPIView,
    PostLikeToggleAPIView,
    ProfileDetailAPIView,
    RegisterAPIView,
    SearchProfilesAPIView,
)

urlpatterns = [
    path('health/', HealthAPIView.as_view(), name='api-health'),
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('me/', MeAPIView.as_view(), name='api-me'),
    path('posts/', PostCollectionAPIView.as_view(), name='api-posts'),
    path('posts/<uuid:post_id>/', PostDetailAPIView.as_view(), name='api-post-detail'),
    path('posts/<uuid:post_id>/like/', PostLikeToggleAPIView.as_view(), name='api-post-like'),
    path('posts/<uuid:post_id>/comments/', CommentListCreateAPIView.as_view(), name='api-post-comments'),
    path('profiles/<str:username>/', ProfileDetailAPIView.as_view(), name='api-profile-detail'),
    path('search/', SearchProfilesAPIView.as_view(), name='api-search'),
    path('follow/toggle/', FollowToggleAPIView.as_view(), name='api-follow-toggle'),
    path('messages/<str:username>/', MessageThreadAPIView.as_view(), name='api-message-thread'),
    path('messages/', MessageCollectionAPIView.as_view(), name='api-message-create'),
]