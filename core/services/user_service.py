from django.contrib.auth.models import User
from ..models import Profile, FollowersCount


class UserService:
    @staticmethod
    def get_user_by_username(username):
        """Trả về người dùng đầu tiên khớp với username.

        Ghi chú: Hàm cố ý trả về `None` khi không tìm thấy để bên gọi rẽ
        nhánh gọn hơn, không cần bắt `DoesNotExist`.
        """
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_or_create_profile(user):
        """Lấy hoặc tạo profile cho một người dùng.

        Ghi chú: Giá trị mặc định `id_user` bám theo khóa chính của user để
        giữ cho các luồng cũ vẫn chạy được trong lúc chuyển sang FK.
        """
        profile, _ = Profile.objects.get_or_create(user=user, defaults={'id_user': user.id})
        return profile

    @staticmethod
    def is_following(follower_username, user_username):
        """Kiểm tra một username có đang theo dõi username khác hay không.

        Ghi chú: Hàm giải quyết username trước để an toàn với dữ liệu form
        hoặc các nơi gọi chưa có user object.
        """
        follower = User.objects.filter(username=follower_username).first()
        user = User.objects.filter(username=user_username).first()
        if follower is None or user is None:
            return False
        return FollowersCount.objects.filter(follower=follower, user=user).exists()

    @staticmethod
    def followers_count(username):
        """Đếm số người đang theo dõi một username.

        Ghi chú: Trả về `0` cho username không tồn tại để phần render profile
        đơn giản hơn và không phải xử lý ngoại lệ riêng.
        """
        user = User.objects.filter(username=username).first()
        if user is None:
            return 0
        return FollowersCount.objects.filter(user=user).count()
