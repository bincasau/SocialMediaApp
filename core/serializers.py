from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment, FollowersCount, Message, Post, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'id_user', 'bio', 'profileimg', 'location', 'followers_count', 'following_count')

    def get_followers_count(self, obj):
        return getattr(obj, 'followers_count', FollowersCount.objects.filter(user=obj.user).count())

    def get_following_count(self, obj):
        return getattr(obj, 'following_count', FollowersCount.objects.filter(follower=obj.user).count())


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post_id', 'user', 'body', 'created_at')

    def get_post_id(self, obj):
        return str(obj.post_id)


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'caption', 'image', 'created_at', 'no_of_likes', 'comments_count', 'comments')

    def get_comments_count(self, obj):
        return getattr(obj, 'comments_count', obj.comments.count())


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'recipient', 'content', 'timestamp', 'is_read')