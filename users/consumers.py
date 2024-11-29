import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
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
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_id,
            self.channel_name
        )
    
    def receive(self, text_data=None, bytes_data=None):
        from users.views import get_user_profile_by_id
        from users.models import ChannelRecord, Message

        text_data_json = json.loads(text_data)
        action = text_data_json.get('action', 'send-message')

        if action == 'send-message':
            # Existing message send logic
            sender = get_user_profile_by_id(text_data_json['sender'])
            receiver = get_user_profile_by_id(text_data_json['receiver'])
            message = text_data_json['message']
            sent_at = text_data_json['sent_at']
            

            message_instance = Message.objects.create(
                sender=sender.user,
                receiver=receiver.user,
                message=message,
                sent_at=sent_at,
                channel=self.chat_group_id
            )

            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_id,
                {
                    'id': message_instance.id,
                    'type': 'chat_message',
                    'message': message_instance.message,
                    'sender': str(sender.user.id),
                    'receiver': str(receiver.user.id),
                    'sent_at': sent_at,
                }
            )
        elif action == 'mark-as-read':
            message_id = text_data_json['message_id']
            readers_id = text_data_json['readers_id']
            async_to_sync(self.mark_message_as_read)(message_id, readers_id)

        
    def chat_message(self, event):
        id = event['id']
        message = event['message']
        sender = event['sender']
        sent_at = event['sent_at']
        
        self.send(text_data=json.dumps({
            'id': str(id),
            'type': 'message',
            'message': message,
            'sender': str(sender),
            'sent_at': sent_at,
        }))

    @sync_to_async
    def mark_message_as_read(self, message_id, readers_id):
        
        from users.models import Message
        from users.views import get_user_by_id
        
        reader_user = get_user_by_id(readers_id)
        
        try:
            # Fetch the message for the current user
            message = Message.objects.filter(
                id=message_id, 
                receiver=reader_user
            ).first()
            
            print(message)

            if message and not message.is_read:
                message.is_read = True
                message.save()

                # Notify the group about the message status update
                async_to_sync(self.channel_layer.group_send)(
                    self.chat_group_id,
                    {
                        'type': 'message_read',
                        'message_id': message_id,
                    }
                )
        except Exception as e:
            log.error(f"Failed to mark message as read: {e}")

    async def message_read(self, event):
        # Send message read update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message-read',
            'message_id': event['message_id'],
            'status': 'read',
        }))