from django.contrib.auth.models import User
from ..models import Message
from .base import BaseService
from django.db.models import Q


class MessageService(BaseService):
    @staticmethod
    def create_message(sender, recipient_username, content):
        recipient = User.objects.filter(username=recipient_username).first()
        if recipient is None:
            return None
        msg = Message.objects.create(sender=sender, recipient=recipient, content=content)
        return msg

    @staticmethod
    def get_messages_between(user_a, user_b):
        return Message.objects.filter(
            Q(sender=user_a, recipient=user_b) | Q(sender=user_b, recipient=user_a)
        ).order_by('timestamp')
