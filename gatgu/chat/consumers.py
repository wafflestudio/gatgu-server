from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import ChatMessage, ChatMessageImage, ParticipantProfile, Article, OrderChat
from chat.serializers import ChatMessageSerializer, ChatMessageImageSerializer
from firebase_admin import messaging
from push_notification.models import UserFCMToken, FCMToken
from user.models import UserProfile
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import time

import json


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        participant_profiles = [str(item['order_chat_id']) for item in
                                ParticipantProfile.objects.filter(participant_id=self.user_id).values('order_chat_id')]
        articles = [str(item['id']) for item in Article.objects.filter(writer_id=self.user_id).values('id')]

        groups = []
        groups.extend(participant_profiles)
        groups.extend(articles)
        for group in groups:
            self.enter_group(group)

        self.accept()

    def disconnect(self, close_code):
        for group_name in self.groups:
            async_to_sync(self.channel_layer.group_discard)(
                group_name,
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
            self.send(text_data=json.dumps({
                'type': 'PONG'
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
                self.response('ENTER_FAILURE', {'status': 404}, websocket_id)
                return
            if chatting.article.writer_id == user_id:
                self.response('ENTER_SUCCESS', {'status': 200}, websocket_id)
                return
            elif OrderChat.objects.filter(id=chatting_id, participant_profile__participant_id=user_id).exists():
                self.response('ENTER_SUCCESS', {'status': 200}, websocket_id)
                return
            elif chatting.article.article_status == 1:
                ParticipantProfile.objects.create(order_chat=chatting, participant_id=user_id, wish_price=0)
                self.enter_group(room_id)
                self.response('ENTER_SUCCESS', {'status': 201, 'user_id': user_id}, websocket_id)
                user = User.objects.get(id=user_id)
                user_profile = UserProfile.objects.get(user=user)
                msg = {'type': 'system', 'text': user_profile.nickname + ' entered the room', 'image': ''}
                try:
                    serializer = ChatMessageSerializer(data=msg)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(sent_by_id=user_id, chat_id=chatting_id)
                    message_id = ChatMessage.objects.last().id
                    message = ChatMessage.objects.get(id=message_id)
                    async_to_sync(self.channel_layer.group_send)(  # enterance system message
                        room_id,
                        {
                            'type': 'chat_message',
                            'data': ChatMessageSerializer(message).data,
                            'websocket_id': websocket_id
                        }
                    )
                except:
                    self.response('MESSAGE_FAILURE', {}, websocket_id)
                    return
                return
            else:
                self.response('ENTER_FAILURE', {'status': 403}, websocket_id)
                return
            return
        if type == 'EXIT':
            try:
                participant = ParticipantProfile.objects.get(order_chat_id=chatting_id, participant_id=user_id)
                participant.delete()
            except ParticipantProfile.DoesNotExist:
                self.response('EXIT_FAILURE', {'status': 404}, websocket_id)
                return
            self.exit_group(room_id)
            self.response('EXIT_SUCCESS', {'status': 200, 'user_id': user_id}, websocket_id)
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            msg = {'type': 'system', 'text': user_profile.nickname + ' exited the room', 'image': ''}
            try:
                serializer = ChatMessageSerializer(data=msg)
                serializer.is_valid(raise_exception=True)
                serializer.save(sent_by_id=user_id, chat_id=chatting_id)
                message_id = ChatMessage.objects.last().id
                message = ChatMessage.objects.get(id=message_id)
                async_to_sync(self.channel_layer.group_send)(  # enterance system message
                    room_id,
                    {
                        'type': 'chat_message',
                        'data': ChatMessageSerializer(message).data,
                        'websocket_id': websocket_id
                    }
                )
            except:
                self.response('MESSAGE_FAILURE', {}, websocket_id)
                return
            return
        if not room_id in self.groups:
            self.response('MESSAGE_FAILURE', {}, websocket_id)
            return
        msg = data['message']
        msg['type'] = "user"
        try:
            prev_message_time = ChatMessage.objects.filter(chat_id=chatting_id).last().sent_at
            revised_time = prev_message_time+timedelta(hours=9)
            date_msg = revised_time.date()
            date_now = datetime.now().date()
            if date_now != date_msg:
                new_day_msg = {'type': 'system', 'text': date_now, 'image': ''}
                new_day_serializer = ChatMessageSerializer(data=new_day_msg)
                new_day_serializer.is_valid(raise_exception=True)
                new_day_serializer.save(sent_by_id=user_id, chat_id=chatting_id)
                async_to_sync(self.channel_layer.group_send)(
                    room_id,
                    {
                        'type': 'chat_message',
                        'data': ChatMessageSerializer(new_day_msg).data,
                        'websocket_id': websocket_id
                    }
                )
        except:
            pass

        try:
            serializer = ChatMessageSerializer(data=msg)
            serializer.is_valid(raise_exception=True)
            serializer.save(sent_by_id=user_id, chat_id=chatting_id)
            message_id = ChatMessage.objects.last().id
            message = ChatMessage.objects.get(id=message_id)
            if 'image' in msg and msg['image'] != '':
                message.image.create(img_url=msg['image'])
            message.save()
            message = ChatMessage.objects.get(id=message_id)
            async_to_sync(self.channel_layer.group_send)(
                room_id,
                {
                    'type': 'chat_message',
                    'data': ChatMessageSerializer(message).data,
                    'websocket_id': websocket_id
                }
            )

            sandbox = True

            # 희수 안드 에뮬
            token = 'cgcEjP3DRaaLakdcasEh5l:APA91bExlss0NmSZMBaiKuZDUVrNHROYba6o92fj8C8G10Phs2dPLji-AWK30uI6pbS1n5q7IoAdfi3FOM9ISShhtHWQTZWwE42WKWAG7XY4fQjsG_HdgH35ApRgSQF0hu1V2bBAaz9u'

            if sandbox:
                self.send_notification(msg, room_id, token)
                return
            # 1. 해당 채팅방 user id 다 가져옴 
            chatting = OrderChat.objects.get(id=chatting_id)
            participants = [participant['participant_id'] for participant in
                            ParticipantProfile.objects.filter(order_chat_id=chatting_id).values('participant_id')]
            participants.append(chatting.article.writer_id)
            # 2. user id에 해당하는 token 전부 가져옴
            tokens_id = [user_token['token_id'] for user_token in
                         UserFCMToken.objects.filter(user_id__in=participants, is_active=True).values('token_id')]
            tokens = [token['fcmtoken'] for token in FCMToken.objects.filter(id__in=tokens_id).values('fcmtoken')]
            # 3. 해당 token들로 알림 Push
            for token in tokens:
                self.send_notification(msg, room_id, token)
            return
        except:
            self.response('MESSAGE_FAILURE', {}, websocket_id)
            return

    def send_notification(self, msg, room_id, token):
        payload = {
            'params': {
                'room_id': room_id
            }
        }
        jspayload = json.dumps(payload, separators=(',', ':'))
        message = messaging.Message(
            notification=messaging.Notification(
                title=msg['text'],
                body=msg['image'],
            ),
            data={
                'link': "gatgu://chatting/" + room_id,
                # 'path': "ChattingRoomStack/ChattingRoom",
                'type': 'chatting',
                'payload': jspayload
            },
            token=token,
        )
        response = messaging.send(message)
        return response

    def chat_message(self, event):
        data = event['data']
        websocket_id = event['websocket_id']
        
        self.send(text_data=json.dumps({
            'data': data,
            'type': 'MESSAGE_SUCCESS',
            'websocket_id': websocket_id
        }))

    def change_status(self, event):
        data = event['data']
        self.send(text_data=json.dumps({
            'data': data,
            'type': 'UPDATE_STATUS'
        }))

    def response(self, type, data, websocket_id):
        self.send(text_data=json.dumps({
            'type': type,
            'data': data,
            'websocket_id': websocket_id
        }))

    def pong(self, event):
        self.send(text_data=json.dumps({
            'data': 'data',
            'type': 'PONG'
        }))
