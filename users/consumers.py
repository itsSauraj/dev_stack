import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer

log = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    
    def connect(self):
        
        from users.views import UserView
        update_online_status = UserView.update_online_status
        
        self.user_socket_id = self.scope['url_route']['kwargs']['group_id']
        self.chat_group_id = f"{self.scope['user'].id}"

        # When creating groups for future use, use the following code        
        # async_to_sync(self.channel_layer.group_add)(
        #     self.chat_group_id,
        #     self.channel_name
        # )
        async_to_sync(self.channel_layer.group_add)(
            self.user_socket_id,
            self.channel_name
        )
        
        self.accept()    
        online_status = update_online_status(self.chat_group_id, self.user_socket_id, True)


    def disconnect(self, close_code):
        
        from users.views import update_online_status
        
        if hasattr(self.scope, 'user_groups'):
            for group in self.scope['user_groups']:
                online_status = update_online_status(self.group.id, None, False)
                async_to_sync(self.channel_layer.group_discard)(
                    group,
                    self.channel_name
                )
    
    def receive(self, text_data=None, bytes_data=None):
        from users.views import UserView, Channel
        
        get_user_profile_by_id = UserView.get_user_profile_by_id
        from users.models import Message, ChatRecords

        text_data_json = json.loads(text_data)
        action = text_data_json.get('action', 'send-message')

        if action == 'send-message':
            # Existing message send logic
            sender = get_user_profile_by_id(text_data_json['sender'])
            receiver = get_user_profile_by_id(text_data_json['receiver'])
            message = text_data_json['message']
            sent_at = text_data_json['sent_at']
            chat_room_id = text_data_json['chat_room_id']
            
            chat_room = ChatRecords.objects.filter(id=chat_room_id).first()
            

            message_instance = Message.objects.create(
                sender=sender.user,
                receiver=receiver.user,
                message=message,
                sent_at=sent_at,
                chat_id=chat_room,
            )
            
            count_unread = Message.objects.filter(receiver=receiver.user, is_read=False, 
                                                  chat_id=chat_room.id).count()
            
            message = {
                'id': message_instance.id,
                'type': 'chat_message',
                'message': message_instance.message,
                'sender': str(sender.user.id),
                'receiver': str(receiver.user.id),
                'sent_at': sent_at,
                'chat_room_id': str(chat_room.id),
            }

            async_to_sync(self.channel_layer.group_send)(
                self.user_socket_id,
                message
            )
            
            if receiver.user.is_online:
                message['unread_message_count'] = int(count_unread)
                async_to_sync(self.channel_layer.group_send)(
                    receiver.user.socket_id,
                    message
                )
                self.notify_user(receiver.user, message['message'], sender.user)
                message_instance.mark_as_sent()
                async_to_sync(self.channel_layer.group_send)(
                    self.user_socket_id,
                    {
                        'type': 'message_sent',
                        'message_id': str(message_instance.id),
                    }
                )
            
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
                    sender = message.sender
                    receiver = message.receiver
                    chat_room = message.chat_id
                    message.save()

                    response =       {
                        'type': 'message_read',
                        'message_id': message_id,
                        'chat_room_id': str(chat_room.id),
                    }
                    async_to_sync(self.channel_layer.group_send)(
                        sender.socket_id,
                        response
                    )
                    
                    unread_message_count = Message.objects.filter(receiver=receiver, is_read=False, 
                                                  chat_id=chat_room.id).count()
                    
                    response['unread_message_count'] = unread_message_count
                    
                    async_to_sync(self.channel_layer.group_send)(
                        receiver.socket_id,
                        response
                    )
                        
            except Exception as e:
                log.error(f"Failed to mark message as read: {e}")

        
    def chat_message(self, event):
        id = event['id']
        message = event['message']
        sender = event['sender']
        sent_at = event['sent_at']
        receiver = event['receiver']
        chat_room_id = event['chat_room_id']
        unread_message_count = event.get('unread_message_count', 0)
        
        self.send(text_data=json.dumps({
            'id': str(id),
            'type': 'message',
            'message': message,
            'sender': str(sender),
            'sent_at': sent_at,
            'receiver': str(receiver),
            'chat_room_id': chat_room_id,
            'unread_message_count': unread_message_count,
        }))

    def message_read(self, event):
        message_id = event['message_id']
        chat_room_id = event.get('chat_room_id')
        unread_message_count = event.get('unread_message_count', 0)
        
        self.send(text_data=json.dumps({
            'type': 'message-read',
            'message_id': message_id,
            'status': 'read',
            'unread_message_count': unread_message_count,
            'chat_room_id': str(chat_room_id),
        }))
        
    def message_sent(self, event):
        message_id = event['message_id']
        
        self.send(text_data=json.dumps({
            'type': 'message-sent',
            'message_id': message_id,
            'status': 'sent',
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
            recipient.socket_id,
            {
                'type': 'notification',
                'notification': notification,
                'recipient': str(recipient.id),
            }
        )
    
    def notification(self, event):
        notification = event['notification']

        
        if notification['sender'] != self.scope['user'].id:
            self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification,
            }))