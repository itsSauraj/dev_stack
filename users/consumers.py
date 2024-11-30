import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer

log = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        self.chat_group_id = self.scope['url_route']['kwargs']['group_id']  
        
        if not hasattr(self.scope, 'user_groups'):
            self.scope['user_groups'] = set()

        self.scope['user_groups'].add(self.chat_group_id)

        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_id,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self.scope, 'user_groups'):
            for group in self.scope['user_groups']:
                async_to_sync(self.channel_layer.group_discard)(
                    group,
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
            
            self.notify_user(receiver.user, message, sender.user)
            
        elif action == 'mark-as-read':
            from users.models import Message
            
            message_id = text_data_json['message_id']
            readers_id = text_data_json['readers_id']
            
            try:
                message = Message.objects.filter(
                    id=message_id, 
                    receiver__id=readers_id
                ).first()
                
                if not message.is_read:
                    message.is_read = True
                    message.save()

                    async_to_sync(self.channel_layer.group_send)(
                        self.chat_group_id,
                        {
                            'type': 'message_read',
                            'message_id': message_id,
                        }
                    )
            except Exception as e:
                log.error(f"Failed to mark message as read: {e}")

        
    def chat_message(self, event):
        id = event['id']
        message = event['message']
        sender = event['sender']
        sent_at = event['sent_at']
        receiver = event['receiver']
        
        self.send(text_data=json.dumps({
            'id': str(id),
            'type': 'message',
            'message': message,
            'sender': str(sender),
            'sent_at': sent_at,
            'receiver': str(receiver),
        }))

    def message_read(self, event):
        
        message_id = event['message_id']
        
        self.send(text_data=json.dumps({
            'type': 'message-read',
            'message_id': message_id,
            'status': 'read',
        }))
        
    def notify_user(self, recipient, message, sender):
        notification = {
            'type': 'notification',
            'title': 'New Message',
            'body': f'{sender.username} sent you a message: {message[:20]}',
            'sender': str(sender.id),
        }

        # Notify the user's WebSocket group
        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_id,
            {
                'type': 'notification',
                'notification': notification,
            }
        )
    
    def notification(self, event):
        notification = event['notification']
        
        if notification['sender'] != self.scope['user'].id:
            self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification,
            }))