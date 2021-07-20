from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import ChatMessage, ChatMessageImage, ParticipantProfile, Article, OrderChat
from chat.serializers import ChatMessageSerializer, ChatMessageImageSerializer
import json

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
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
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        if type == 'PING':
            self.send(text_data = json.dumps({
                'type' : 'PONG'
            }))
            return
        websocket_id = text_data_json['websocket_id']
        data = text_data_json['data']
        chatting_id = data['room_id']
        room_id = str(chatting_id)
        user_id = int(data['user_id'])
        if type == 'ENTER':
            try:
                chatting = OrderChat.objects.get(id=chatting_id)
            except OrderChat.DoesNotExist:
                self.response('ENTER_FAILURE', 404, websocket_id)
                return
            
            if chatting.article.writer_id == user_id:
                self.response('ENTER_SUCCESS', 200, websocket_id)
                return
            elif OrderChat.objects.filter(id=chatting_id, participant_profile__participant_id=user_id).exists():
                self.response('ENTER_SUCCESS', 200, websocket_id)
                return
            elif chatting.order_status==1:
                ParticipantProfile.objects.create(order_chat=chatting, participant_id=user_id, wish_price=0)
                self.response('ENTER_SUCCESS', 201, websocket_id)

                self.enter_group(room_id)
                msg = {'type' : 'system', 'text': 'enter_room', 'img' : ''}
                try:
                    serializer = ChatMessageSerializer(data=msg)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(sent_by_id=user_id, chat_id=chatting_id)
                    message_id = ChatMessage.objects.last().id
                    message = ChatMessage.objects.get(id=message_id)
                    async_to_sync(self.channel_layer.group_send)( # enterance system message
                        str(chatting_id),
                        {
                            'type': 'chat_message',
                            'data': ChatMessageSerializer(message).data,
                            'websocket_id' : websocket_id
                        }
                    )
                except:
                    self.response('MESSAGE_FAILURE', '', websocket_id)
                    return
                return
            else:
                self.response('ENTER_FAILURE', 403, websocket_id)
                return
            return
        if type == 'EXIT':
            try:
                participant = ParticipantProfile.objects.get(order_chat_id=chatting_id, participant_id=user_id)
                participant.delete()
            except ParticipantProfile.DoesNotExist:
                self.response('EXIT_FAILURE', 404, websocket_id)
                return 
            self.exit_group(room_id)
            self.response('EXIT_SUCCESS', 200, websocket_id)
            msg = {'type' : 'system', 'text': 'exit_room', 'img' : ''}
            try:
                serializer = ChatMessageSerializer(data=msg)
                serializer.is_valid(raise_exception=True)
                serializer.save(sent_by_id=user_id, chat_id=chatting_id)
                message_id = ChatMessage.objects.last().id
                message = ChatMessage.objects.get(id=message_id)
                async_to_sync(self.channel_layer.group_send)( # enterance system message
                    str(chatting_id),
                    {
                        'type': 'chat_message',
                        'data': ChatMessageSerializer(message).data,
                        'websocket_id' : websocket_id
                    }
                )
            except:
                self.response('MESSAGE_FAILURE', '', websocket_id)
                return
            return
        if not room_id in self.groups:
            return

        msg = data['message']
        msg['type'] = "user"
        try:
            serializer = ChatMessageSerializer(data=msg)
            serializer.is_valid(raise_exception=True)
            serializer.save(sent_by_id=user_id, chat_id=chatting_id)
            message_id = ChatMessage.objects.last().id
            message = ChatMessage.objects.get(id=message_id)

            if msg['img'] != '':
                message.image.create(img_url=msg['img'])
            message.save()
            message = ChatMessage.objects.get(id=message_id)
            async_to_sync(self.channel_layer.group_send)(
                str(chatting_id),
                {
                    'type': 'chat_message',
                    'data': ChatMessageSerializer(message).data,
                    'websocket_id' : websocket_id
                }
            )
        except:
            self.response('MESSAGE_FAILURE', '', websocket_id)
            return
    
    def chat_message(self, event):
        data = event['data']
        websocket_id = event['websocket_id']
        self.send(text_data=json.dumps({
            'data' : data,
            'type' : 'MESSAGE_SUCCESS',
            'websocket_id' : websocket_id
        }))
    
    def response(self, type, data, websocket_id):
        self.send(text_data=json.dumps({
            'type' : type,
            'data' : data,
            'websocket_id' : websocket_id
        }))
    
    def pong(self, event):
        self.send(text_data=json.dumps({
            'data' : 'data',
            'type' : 'PONG'
        }))
    