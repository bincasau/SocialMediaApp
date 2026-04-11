from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.setting, name='setting'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('signup', views.signup, name='signup'),
    path('like-post', views.like_post, name='like-post'),
    path('comment', views.comment_post, name='comment'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
]