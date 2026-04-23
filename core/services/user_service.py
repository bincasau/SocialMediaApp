from django.contrib.auth.models import User
from ..models import Profile, FollowersCount


class UserService:
    @staticmethod
    def get_user_by_username(username):
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_or_create_profile(user):
        profile, _ = Profile.objects.get_or_create(user=user, defaults={'id_user': user.id})
        return profile

    @staticmethod
    def is_following(follower_username, user_username):
        return FollowersCount.objects.filter(follower=follower_username, user=user_username).exists()

    @staticmethod
    def followers_count(username):
        return FollowersCount.objects.filter(user=username).count()
