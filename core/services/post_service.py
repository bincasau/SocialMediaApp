from .base import BaseService
from ..models import Post, Comment, LikePost


class PostService(BaseService):
    @staticmethod
    def get_post_by_id(post_id):
        return Post.objects.filter(id=post_id).first()

    @staticmethod
    def create_comment(post, username, body):
        return Comment.objects.create(post=post, username=username, body=body)

    @staticmethod
    def toggle_like(post, username):
        like = LikePost.objects.filter(post_id=post.id, username=username).first()
        if like is None:
            LikePost.objects.create(post_id=post.id, username=username)
            post.no_of_likes = post.no_of_likes + 1
            post.save()
            return True
        else:
            like.delete()
            post.no_of_likes = max(0, post.no_of_likes - 1)
            post.save()
            return False
