import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

log = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = dict(qc.split('=') for qc in query_string.split('&'))
        self.chat_group_id = query_params.get('id', 'unknown')

        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_id,
            self.channel_name
        )
        
        self.accept()

        self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'You are connected to the chat room',
            'group_name': self.chat_group_id,
        }))
        
    
    def receive(self, text_data=None, bytes_data=None):
        
        from users.views import get_user_profile_by_id
        from users.models import ChannelRecord, Message
        
        text_data_json = json.loads(text_data)
        
        sender = get_user_profile_by_id(text_data_json['sender_id'])
        message = text_data_json['message']
        sent_at = text_data_json['sent_at']
        
        
        Message.objects.create(
            sender=sender.user,
            message=message,
            sent_at=sent_at,
            channel=self.chat_group_id
        )        
        
        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_id,
            {
                'type': 'chat_message',
                'message': message,
                'sender': str(sender.user.id),
                'sent_at': sent_at,
            }
        )
        
    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        sent_at = event['sent_at']
        
        self.send(text_data=json.dumps({
            'type': 'received-message',
            'message': message,
            'sender': str(sender),
            'sent_at': sent_at,
        }))