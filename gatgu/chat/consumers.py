from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import ChatMessage, ChatMessageImage, ParticipantProfile, Article
from chat.serializers import ChatMessageSerializer, ChatMessageImageSerializer
import json

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.self_response = 'ping_'+str(user_id)
        self.enter_group(self.self_response)
        #self.chat_group_name = 'chat_%s' % self.chat_id
        
        participant_profiles = [str(item['order_chat_id']) for item in ParticipantProfile.objects.filter(participant_id = self.user_id).values('order_chat_id')]
        articles = [str(item['id']) for item in Article.objects.filter(writer_id = self.user_id).values('id')]
        
        groups = []
        groups.extend(participant_profiles)
        groups.extend(articles)

        for group in groups:
            self.enter_group(group)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def enter_group(self, group_name):
        if group_name in self.groups:
            return {'type': 'ENTER_FAILURE'}
        async_to_sync(self.channel_layer.group_add)(
            group_name,
            self.channel_name
        )
        self.groups.append(group_name)
        return {'type': 'ENTER_SUCCESS'}
        #print(self.groups)
    
    def exit_group(self, group_name):
        if not group_name in self.groups:
            return {'type': 'EXIT_FAILURE'}
        async_to_sync(self.channel_layer.group_discard)(
            group_name,
            self.channel_name
        )
        self.groups.remove(group_name)
        return {'type': 'EXIT_SUCCESS'}

    def receive(self, text_data):
        print(self.groups)
        text_data_json = json.loads(text_data)
        print(text_data_json)
        type = text_data_json['type']
        if type == 'PING': # 자신한테만 보내야함 => self.self_group을 만들자
            print('ping')
            async_to_sync(self.channel_layer.group_send)(
                self.self_response,
                {'type': 'pong'}
            )
            return
        
        data = text_data_json['data']
        chatting_id = data['room_id']
        room_id = str(chatting_id)
        user_id = data['user_id']
        if type == 'ENTER':
            print(room_id)
            response = self.enter_group(room_id)
            async_to_sync(self.channel_layer.group_send){
                self.self_response,
                response
            }
            return
        if type == 'EXIT':
            response = self.exit_group(room_id)
            async_to_sync(self.channel_layer.group_send){
                self.self_response,
                response
            }
            return

        if not room_id in self.groups:
            return

        msg = data['message']
        serializer = ChatMessageSerializer(data=msg)
        serializer.is_valid(raise_exception=True)
        serializer.save(sent_by_id=user_id, chat_id=chatting_id)
        print(3)
        print(serializer.data)
        print(5)
        message_id = ChatMessage.objects.last().id
        message = ChatMessage.objects.get(id=message_id)
        print(4)
        #print(data)
        #print(message['text'])
        print(msg)
        if msg['img'] != '':
            print(msg)
            message.image.create(img_url=msg['img'])
            message.save()
        print(2)
        print(5)
        print(4)
        a = ChatMessageSerializer(message).data
        print(self.channel_layer)
        print(chatting_id)
        print(self.groups)
        async_to_sync(self.channel_layer.group_send)(
            str(chatting_id),
            {
                'type': 'chat_message',
                'data': a
            }
        )

    def chat_message(self, event):
        data = event['data']

        self.send(text_data=json.dumps({
            'data' : data
        }))
    
    def pong(self, event):

        self.send(text_data=json.dumps({
            'data' : 'data',
            'type' : 'PONG'
        }))
    
        