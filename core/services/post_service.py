from .base import BaseService
from ..models import Post, Comment, LikePost
from .user_service import UserService


class PostService(BaseService):
    @staticmethod
    def get_post_by_id(post_id):
        """Lấy bài viết theo khóa chính.

        Ghi chú: Trả về `None` thay vì ném lỗi để bên gọi xử lý bài viết
        không tồn tại mà không cần bọc `try/except`.
        """
        return Post.objects.filter(id=post_id).first()

    @staticmethod
    def create_comment(post, user, body):
        """Tạo bình luận cho bài viết bằng user object hoặc username.

        Ghi chú: Hỗ trợ cả hai dạng để các chỗ gọi cũ vẫn chạy trong lúc
        codebase đang chuyển sang dùng foreign key rõ ràng.
        """
        if isinstance(user, str):
            user = UserService.get_user_by_username(user)
        if user is None:
            return None
        return Comment.objects.create(post=post, user=user, body=body)

    @staticmethod
    def toggle_like(post, user):
        """Bật hoặc tắt lượt thích cho bài viết và người dùng tương ứng.

        Ghi chú: Hàm này cập nhật luôn bộ đếm like để test và view không bị
        lệch với dữ liệu đã lưu.
        """
        if isinstance(user, str):
            user = UserService.get_user_by_username(user)
        if user is None:
            return False

        like = LikePost.objects.filter(post=post, user=user).first()
        if like is None:
            LikePost.objects.create(post=post, user=user)
            post.no_of_likes = post.no_of_likes + 1
            post.save()
            return True
        else:
            like.delete()
            post.no_of_likes = max(0, post.no_of_likes - 1)
            post.save()
            return False
