from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import ChatMessage, ChatMessageImage
from chat.serializers import ChatMessageSerializer, ChatMessageImageSerializer
import json

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = 'chat_%s' % self.chat_id

        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        user_id = text_data_json['user_id']

        serializer = ChatMessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sent_by_id=user_id, chat_id=self.chat_id)
        message_id = ChatMessage.objects.last().id
        message = ChatMessage.objects.get(id=message_id)

        if data['image'] != '':
            message.image.create(img_url=data['image'])
            message.save()

        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'data': data
            }
        )

    def chat_message(self, event):
        data = event['data']

        self.send(text_data=json.dumps({
            'data' : data
        }))
        