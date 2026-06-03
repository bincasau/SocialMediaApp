from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, FollowersCount, LikePost, Message, Post, Profile
from .serializers import CommentSerializer, MessageSerializer, PostSerializer, ProfileSerializer, UserSerializer
from .services.message_service import MessageService
from .services.post_service import PostService


def _get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'id_user': user.id})
    return profile


def _api_auth_classes():
    return [BasicAuthentication, SessionAuthentication]


class BaseAPIView(APIView):
    authentication_classes = _api_auth_classes()


class PublicAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class HealthAPIView(PublicAPIView):
    def get(self, request):
        return Response({'ok': True})


class RegisterAPIView(PublicAPIView):
    def post(self, request):
        username = (request.data.get('username') or '').strip()
        email = (request.data.get('email') or '').strip()
        password = request.data.get('password') or ''
        password2 = request.data.get('password2') or ''

        if not username or not email or not password:
            return Response({'ok': False, 'error': 'Missing username, email, or password'}, status=status.HTTP_400_BAD_REQUEST)

        if password != password2:
            return Response({'ok': False, 'error': 'Password not matching'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'ok': False, 'error': 'Email already used'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'ok': False, 'error': 'Username already used'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = _get_or_create_profile(user)
        login(request, user)

        return Response(
            {'ok': True, 'user': UserSerializer(user).data, 'profile': ProfileSerializer(profile).data},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(PublicAPIView):
    def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'ok': False, 'error': 'Credentials Invalid'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        profile = _get_or_create_profile(user)
        return Response({'ok': True, 'user': UserSerializer(user).data, 'profile': ProfileSerializer(profile).data})


class LogoutAPIView(BaseAPIView):
    def post(self, request):
        logout(request)
        return Response({'ok': True})


class MeAPIView(BaseAPIView):
    def get(self, request):
        profile = _get_or_create_profile(request.user)
        return Response({'ok': True, 'user': UserSerializer(request.user).data, 'profile': ProfileSerializer(profile).data})


class PostCollectionAPIView(BaseAPIView):
    def get(self, request):
        scope = (request.query_params.get('scope') or 'feed').strip().lower()

        if scope == 'all':
            posts = Post.objects.select_related('user').prefetch_related('comments__user').order_by('-created_at')
        else:
            following_ids = FollowersCount.objects.filter(follower=request.user).values_list('user_id', flat=True)
            posts = Post.objects.filter(Q(user=request.user) | Q(user_id__in=following_ids)).select_related('user').prefetch_related('comments__user').distinct().order_by('-created_at')

        return Response({'ok': True, 'posts': PostSerializer(posts, many=True, context={'request': request}).data})

    def post(self, request):
        image = request.FILES.get('image_upload') or request.FILES.get('image')
        caption = (request.data.get('caption') or '').strip()

        if image is None or not caption:
            return Response({'ok': False, 'error': 'Missing image or caption'}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.create(user=request.user, image=image, caption=caption)
        return Response({'ok': True, 'post': PostSerializer(post, context={'request': request}).data}, status=status.HTTP_201_CREATED)


class PostDetailAPIView(BaseAPIView):
    def get(self, request, post_id):
        post = Post.objects.select_related('user').prefetch_related('comments__user').filter(id=post_id).first()
        if post is None:
            return Response({'ok': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'ok': True, 'post': PostSerializer(post, context={'request': request}).data})


class PostLikeToggleAPIView(BaseAPIView):
    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            return Response({'ok': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        liked = PostService.toggle_like(post, request.user)
        return Response({'ok': True, 'liked': liked, 'no_of_likes': post.no_of_likes})


class CommentListCreateAPIView(BaseAPIView):
    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            return Response({'ok': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')
        return Response({'ok': True, 'comments': CommentSerializer(comments, many=True).data})

    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post is None:
            return Response({'ok': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        body = (request.data.get('body') or request.data.get('comment') or '').strip()
        if not body:
            return Response({'ok': False, 'error': 'Missing comment body'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(post=post, user=request.user, body=body)
        return Response({'ok': True, 'comment': CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)


class ProfileDetailAPIView(BaseAPIView):
    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'ok': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.filter(user=user).first()
        if profile is None:
            profile = _get_or_create_profile(user)

        profile.followers_count = FollowersCount.objects.filter(user=user).count()
        profile.following_count = FollowersCount.objects.filter(follower=user).count()

        posts = Post.objects.filter(user=user).select_related('user').prefetch_related('comments__user').order_by('-created_at')
        return Response(
            {
                'ok': True,
                'profile': ProfileSerializer(profile).data,
                'posts': PostSerializer(posts, many=True, context={'request': request}).data,
                'post_count': posts.count(),
            }
        )


class SearchProfilesAPIView(BaseAPIView):
    def get(self, request):
        query = (request.query_params.get('q') or request.query_params.get('username') or '').strip()
        if not query:
            return Response({'ok': True, 'results': []})

        profiles = Profile.objects.filter(user__username__icontains=query).select_related('user').order_by('user__username')
        usernames = [profile.user.username for profile in profiles]
        follower_counts = {
            row['user__username']: row['total']
            for row in FollowersCount.objects.filter(user__username__in=usernames).values('user__username').annotate(total=Count('id'))
        }

        results = []
        for profile in profiles:
            profile.followers_count = follower_counts.get(profile.user.username, 0)
            profile.following_count = FollowersCount.objects.filter(follower=profile.user).count()
            results.append(ProfileSerializer(profile).data)

        return Response({'ok': True, 'query': query, 'results': results})


class FollowToggleAPIView(BaseAPIView):
    def post(self, request):
        target_username = (request.data.get('username') or request.data.get('user') or request.data.get('target_username') or '').strip()
        if not target_username:
            return Response({'ok': False, 'error': 'Missing username'}, status=status.HTTP_400_BAD_REQUEST)

        target_user = User.objects.filter(username=target_username).first()
        if target_user is None:
            return Response({'ok': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        relation = FollowersCount.objects.filter(follower=request.user, user=target_user).first()
        if relation is None:
            FollowersCount.objects.create(follower=request.user, user=target_user)
            following = True
        else:
            relation.delete()
            following = False

        return Response(
            {
                'ok': True,
                'following': following,
                'followers_count': FollowersCount.objects.filter(user=target_user).count(),
                'following_count': FollowersCount.objects.filter(follower=target_user).count(),
            }
        )


class MessageThreadAPIView(BaseAPIView):
    def get(self, request, username):
        other_user = User.objects.filter(username=username).first()
        if other_user is None:
            return Response({'ok': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        messages_qs = MessageService.get_messages_between(request.user, other_user)
        return Response({'ok': True, 'messages': MessageSerializer(messages_qs, many=True).data})


class MessageCollectionAPIView(BaseAPIView):
    def post(self, request):
        recipient_username = (request.data.get('recipient') or '').strip()
        content = (request.data.get('message') or request.data.get('content') or '').strip()

        if not recipient_username or not content:
            return Response({'ok': False, 'error': 'Missing recipient or content'}, status=status.HTTP_400_BAD_REQUEST)

        msg = MessageService.create_message(request.user, recipient_username, content)
        if msg is None:
            return Response({'ok': False, 'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'ok': True, 'message': MessageSerializer(msg).data}, status=status.HTTP_201_CREATED)
