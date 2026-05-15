from django.db import models
from django.contrib.auth import get_user_model
import uuid
from PIL import Image
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    """
    Model Profile lưu trữ thông tin mở rộng của người dùng.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='default-profile.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """
        Trả về string đại diện cho Profile (thường là username).

        Ghi chú: `__str__` nên nhẹ vì Django có thể gọi nó ở trang admin,
        log và khi debug.
        """
        return self.user.username
        
    def save(self, *args, **kwargs):
        """
        Ghi đè hàm save để thu nhỏ kích thước ảnh tự động khi upload ảnh đại diện.

        Ghi chú: Bỏ qua bước resize nếu không có file để test và các lần cập
        nhật một phần không bị lỗi vì thiếu media.
        """
        super().save(*args, **kwargs)
        if not self.profileimg:
            return

        try:
            img = Image.open(self.profileimg.path)
        except (FileNotFoundError, ValueError, OSError):
            return

        if img.height > 300 or img.width > 300:
            img.thumbnail((300, 300))
            img.save(self.profileimg.path)
    
class Post(models.Model):
    """
    Model Post lưu trữ thông tin về bài viết của người dùng.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Sửa từ CharField sang ForeignKey để liên kết chính xác với User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        """
        Trả về string đại diện cho Post.

        Ghi chú: Phần xem trước được giữ ngắn để admin và debug vẫn dễ đọc dù
        caption dài.
        """
        return f"{self.user.username}'s post: {self.caption[:20]}"

    def save(self, *args, **kwargs):
        """
        Ghi đè hàm save để thu nhỏ ảnh bài đăng tránh tốn dung lượng server (tối đa 800px).

        Ghi chú: Cách này giúp ảnh upload gọn hơn mà không bắt bên gọi phải
        xử lý ảnh thủ công trước khi lưu.
        """
        super().save(*args, **kwargs)
        if not self.image:
            return

        try:
            img = Image.open(self.image.path)
        except (FileNotFoundError, ValueError, OSError):
            return

        if img.height > 800 or img.width > 800:
            img.thumbnail((800, 800))
            img.save(self.image.path)

class LikePost(models.Model):
    """
    Model LikePost lưu trữ lượt thích của người dùng cho một bài viết.
    """
    # Thay post_id thành ForeignKey tham chiếu tới model Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    # Thay username thành ForeignKey tham chiếu tới model User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')

    def __str__(self):
        """
        Trả về string đại diện thông tin ai đã like post nào.

        Ghi chú: Chuỗi có cả user và post để nhìn quan hệ này rõ hơn trong log.
        """
        return f"{self.user.username} liked {self.post.id}"
    
class FollowersCount(models.Model):
    """
    Model FollowersCount quản lý việc theo dõi người dùng.
    """
    # Người thực hiện hành động theo dõi
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    # Người được theo dõi
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        """
        Trả về string thể hiện mối quan hệ theo dõi.

        Ghi chú: Giữ định dạng dễ đọc sẽ tiện hơn khi xem bảng follow ở admin
        hoặc trong kết quả test.
        """
        return f"{self.follower.username} follows {self.user.username}"


class Comment(models.Model):
    """
    Model Comment lưu trữ bình luận của người dùng trên bài đăng.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # Thay username CharField thành ForeignKey
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Trả về nội dung bình luận ngắn.

        Ghi chú: Định dạng ngắn là đủ cho admin/debug và tránh đổ toàn bộ nội
        dung bình luận ra mọi nơi.
        """
        return f'{self.user.username} on {self.post.id}'


class Message(models.Model):
    """
    Model Message lưu trữ tin nhắn giữa hai người dùng (chat).
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        """
        Trả về thông tin người gửi, nhận và thời gian gửi tin nhắn.

        Ghi chú: Có thêm timestamp để dễ kiểm tra thứ tự hội thoại khi debug.
        """
        return f'Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}'


class Notification(models.Model):
    """
    Model Notification dùng để lưu trữ các thông báo cho người dùng (like, comment, follow).
    """
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('message', 'Message'),
    )
    
    # Người nhận thông báo
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # Người gây ra thông báo (người đã like/comment/follow)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    # Tùy chọn: Link thẳng tới bài post (nếu là like/comment)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    text_preview = models.CharField(max_length=255, blank=True) # Đoạn nội dung ngắn gọn
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """
        Trả về text đại diện cho loại thông báo.

        Ghi chú: Cách này giúp các dòng notification dễ đọc mà không phải bung
        toàn bộ object liên quan.
        """
        return f"{self.sender.username} {self.notification_type} {self.user.username}"


# ================== Signals: Xoá ảnh tự động khi xoá DB ==================
@receiver(post_delete, sender=Profile)
def delete_profile_image(sender, instance, **kwargs):
    """
    Signal (Tín hiệu): Hàm tự động được gọi khi một Profile bị xoá.
    Ghi chú: Xoá file ảnh đại diện trong thư mục vật lý để tiết kiệm dung lượng.
    """
    if instance.profileimg and instance.profileimg.name != 'default-profile.png':
        if os.path.isfile(instance.profileimg.path):
            os.remove(instance.profileimg.path)

@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    """
    Signal (Tín hiệu): Hàm tự động được gọi khi một Post bị xoá.
    Ghi chú: Xoá ảnh của bài đăng đó trong thư mục lưu trữ media.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
