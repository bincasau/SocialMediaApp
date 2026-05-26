from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from core.models import Comment, FollowersCount, LikePost, Message, Post, Profile
from core.services.message_service import MessageService
from core.services.post_service import PostService
from core.services.user_service import UserService

User = get_user_model()


class SocialMediaBasicTests(TestCase):
    """Bộ test hồi quy cơ bản cho các luồng mạng xã hội chính."""

    def setUp(self):
        """Tạo user, profile và bài viết mẫu dùng lại cho các test.

        Ghi chú: Bài viết mẫu dùng ảnh trong bộ nhớ để code xử lý file của
        model chạy được mà không đụng vào thư mục media thật.
        """
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password123')

        self.profile1 = Profile.objects.create(
            user=self.user1,
            id_user=self.user1.id,
            bio='Xin chao, toi la Alice',
            location='Ha Noi',
        )

        self.post = Post.objects.create(
            user=self.user1,
            caption='Bai viet dau tien cua toi!',
            image=self._make_test_image(),
        )

    def _make_test_image(self, name='test-post.png'):
        """Tạo một ảnh PNG nhỏ để test model.

        Ghi chú: Dùng `SimpleUploadedFile` giúp test tự chứa, chạy nhanh và
        vẫn kiểm tra được logic lưu `ImageField`.
        """
        buffer = BytesIO()
        image = Image.new('RGB', (10, 10), color='blue')
        image.save(buffer, format='PNG')
        return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')

    def _log(self, title, details=None):
        """Log kết quả theo format dễ quan sát khi chạy test."""
        message = f"[TEST] {title}"
        if details:
            message = f"{message} | {details}"
        print(message)

    def test_profile_creation(self):
        """Kiểm tra profile được gắn đúng với user tương ứng.

        Ghi chú: Test này bắt lỗi lệch FK giữa `User` và `Profile`.
        """
        profile = Profile.objects.get(user=self.user1)
        self.assertEqual(profile.bio, 'Xin chao, toi la Alice')
        self.assertEqual(profile.user.username, 'alice')
        self._log(
            'Profile creation',
            f"user={profile.user.username}, bio='{profile.bio}'",
        )

    def test_like_post(self):
        """Kiểm tra bật/tắt like có cập nhật đúng bộ đếm bài viết.

        Ghi chú: Service trả về kiểu boolean để bên gọi biết post đang ở trạng
        thái đã thích hay chưa thích.
        """
        liked = PostService.toggle_like(self.post, self.user2)

        self.post.refresh_from_db()
        self.assertTrue(liked)
        self.assertEqual(LikePost.objects.count(), 1)
        self.assertEqual(self.post.no_of_likes, 1)
        self._log(
            'Toggle like',
            f"liked={liked}, likes={self.post.no_of_likes}",
        )

    def test_add_comment(self):
        """Kiểm tra bình luận được tạo đúng với user và bài viết mong muốn.

        Ghi chú: Test này ngăn service vô tình quay lại schema cũ dùng
        username thay vì foreign key.
        """
        comment = PostService.create_comment(self.post, self.user2, 'Tuyet voi qua!')

        self.assertIsNotNone(comment)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.body, 'Tuyet voi qua!')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user2)
        self._log(
            'Add comment',
            f"user={comment.user.username}, body='{comment.body}'",
        )

    def test_follow_user(self):
        """Kiểm tra quan hệ follow và các hàm hỗ trợ hoạt động đúng.

        Ghi chú: Các helper của service được test ở đây để UI profile có thể
        tin vào số lượng follow nhất quán.
        """
        follow = FollowersCount.objects.create(
            follower=self.user2,
            user=self.user1,
        )

        self.assertEqual(FollowersCount.objects.count(), 1)
        self.assertEqual(follow.follower.username, 'bob')
        self.assertEqual(follow.user.username, 'alice')
        self.assertTrue(UserService.is_following('bob', 'alice'))
        self.assertEqual(UserService.followers_count('alice'), 1)
        self._log(
            'Follow user',
            f"follower={follow.follower.username}, user={follow.user.username}, count=1",
        )

    def test_send_message(self):
        """Kiểm tra gửi tin nhắn trực tiếp và truy vấn lại cuộc hội thoại.

        Ghi chú: Test này bao trùm cả tạo tin nhắn lẫn truy vấn hội thoại để
        các endpoint chat dùng chung một đường kiểm chứng.
        """
        msg = MessageService.create_message(self.user2, 'alice', 'Hello Alice, how are you?')
        messages = MessageService.get_messages_between(self.user1, self.user2)

        self.assertIsNotNone(msg)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(msg.sender.username, 'bob')
        self.assertEqual(msg.recipient.username, 'alice')
        self.assertEqual(msg.content, 'Hello Alice, how are you?')
        self.assertFalse(msg.is_read)
        self.assertEqual(messages.count(), 1)
        self._log(
            'Send message',
            f"from={msg.sender.username}, to={msg.recipient.username}, total={messages.count()}",
        )
