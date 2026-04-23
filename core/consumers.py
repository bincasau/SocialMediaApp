import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from .services.message_service import MessageService
from .services.user_service import UserService

User = get_user_model()


def _room_name_for_users(user1, user2):
    usernames = sorted([user1.username, user2.username])
    return f'chat_{usernames[0]}_{usernames[1]}'


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        print("WEBSOCKET CONNECTED")

        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_user = await database_sync_to_async(UserService.get_user_by_username)(self.other_username)
        if not self.other_user:
            await self.close()
            return

        self.room_name = _room_name_for_users(self.user, self.other_user)
        self.group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        data = json.loads(text_data)
        message = data.get('message')

        if not message:
            return

        # persist message
        msg = await database_sync_to_async(MessageService.create_message)(self.user, self.other_user.username, message)
        if msg is None:
            return

        out = {
            'id': msg.id,
            'sender': self.user.username,
            'recipient': self.other_user.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
        }

        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': out
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
