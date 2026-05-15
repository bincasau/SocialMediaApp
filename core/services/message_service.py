from django.contrib.auth import get_user_model
from ..models import Message
from .base import BaseService
from django.db.models import Q

User = get_user_model()


class MessageService(BaseService):
    @staticmethod
    def create_message(sender, recipient, content):
        """Tạo tin nhắn trực tiếp giữa hai người dùng.

        Ghi chú: `recipient` có thể là chuỗi username để tương thích với
        các view và test đang truyền thẳng dữ liệu từ form.
        """
        if isinstance(recipient, str):
            recipient = User.objects.filter(username=recipient).first()
        if recipient is None:
            return None
        msg = Message.objects.create(sender=sender, recipient=recipient, content=content)
        return msg

    @staticmethod
    def get_messages_between(user_a, user_b):
        """Trả về lịch sử chat giữa hai người dùng theo thứ tự thời gian.

        Ghi chú: Sắp xếp ngay tại đây để mọi nơi gọi đều nhận cùng một thứ tự
        hội thoại ổn định.
        """
        return Message.objects.filter(
            Q(sender=user_a, recipient=user_b) | Q(sender=user_b, recipient=user_a)
        ).order_by('timestamp')
