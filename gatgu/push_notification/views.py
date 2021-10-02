import json

from django.db import transaction, IntegrityError
from django.shortcuts import render

from firebase_admin import messaging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from push_notification.models import UserFCMToken, FCMToken


class FCMViewSet(viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)

    @transaction.atomic
    def create(self, request):
        user = request.user
        data = request.data

        # comes from Client
        token = data.get('token')

        if FCMToken.objects.filter(fcmtoken=token).exists(): # same device
            return Response({"message: already registered"}, status=status.HTTP_200_OK)
        elif UserFCMToken.objects.filter(user=user).exists():
            user_fcm = UserFCMToken.objects.get(user=user)
            print(user_fcm)
            print(user_fcm.token.fcmtoken)
            tobe_deleted = FCMToken.objects.get(fcmtoken=user_fcm.fcmtoken)
            print(tobe_deleted)
            tobe_deleted.delete()
        FCMToken.objects.create(fcmtoken=token)
        token_obj = FCMToken.objects.last()
        try:
            UserFCMToken.objects.create(user=user, token=token_obj)
        except IntegrityError:
            return Response({"message: you already have this token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message: This token Successfully registered"}, status=status.HTTP_201_CREATED)
    
    @action(methods=['PUT'], detail=False)
    def activate(self, request):
        user = request.user
        data = request.data
        
        try:
            user_token = UserFCMToken.objects.get(user=user)
            active = data['active']
            user_token.is_active = active
            user_token.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=False)
    def messaging(self, request):
        user = request.user

        # 희수 안드 에뮬
        token = 'cgcEjP3DRaaLakdcasEh5l:APA91bExlss0NmSZMBaiKuZDUVrNHROYba6o92fj8C8G10Phs2dPLji-AWK30uI6pbS1n5q7IoAdfi3FOM9ISShhtHWQTZWwE42WKWAG7XY4fQjsG_HdgH35ApRgSQF0hu1V2bBAaz9u'
        # token = UserFCMToken.objects.filter(user=request.user, is_active=True)
        # See documentation on defining a message payload.

        payload = {
            'params': {
                'room_id': '1'
            }
        }
        jspayload = json.dumps(payload, separators=(',', ':'))
        message = messaging.Message(
            notification=messaging.Notification(
                title='안녕하세요 메세지 잘 도착했습니까???',
                body='그렇다면 소리질러..',
            ),
            data={
                'link': "gatgu://chatting/:room_id",
                'path': "ChattingRoomStack/ChattingRoom",
                'type': 'chatting',
                'payload': jspayload
            },
            token=token,
        )
        response = messaging.send(message)
        return Response({'Successfully sent message:%s', response}, status=status.HTTP_200_OK)

    #@action(methods=['PUT'], detail=False, url_path='messaging')
    #def bulk_messaging(self, request):
        # Create a list containing up to 500 registration tokens.
        # These registration tokens come from the client FCM SDKs.
        # registration_tokens = FCMToken.objects.filter(user_fcmtoken__user=request.user).values_list('fcmtoken',
        #                                                                                             flat=True)
        # print(registration_tokens)
        #
        # message = messaging.MulticastMessage(
        #     data={'score': '850', 'time': '2:45'},
        #     tokens=registration_tokens,
        # )
        #
        # response = messaging.send(message)
        #
        # return Response({'Successfully sent message:', response}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='topic')
    def topic(self, request):
        data = request.data
        target_user_id = data.get('user_id')
        tokens = list(FCMToken.objects.filter(user_fcmtoken__user_id=target_user_id).values_list('fcmtoken', flat=True))
        topic = data.get('topic')
        response = messaging.subscribe_to_topic(tokens, topic)
        return Response({'Sucessfully subscribed this topic with token',
                         response.success_count}, status=status.HTTP_201_CREATED)

    # @action(methods=['PUT'], detail=False, url_path='bulk_messaging')
    # def bulk_messaging(self, request):
    #     # Create a list containing up to 500 registration tokens.
    #     # These registration tokens come from the client FCM SDKs.
    #     registration_tokens = list(FCMToken.objects.filter(user_fcmtoken__user=request.user).values_list('fcmtoken',
    #                                                                                                 flat=True))
    #     print(registration_tokens)
    #
    #     message = messaging.MulticastMessage(
    #         data={'score': '850', 'time': '2:45'},
    #         tokens=registration_tokens,
    #     )
    #     response = messaging.send_multicast(message)
    #     # See the BatchResponse reference documentation
    #     # for the contents of response.
    #     print('{0} messages were sent successfully'.format(response.success_count))
    #
    #     # failure check
    #     if response.failure_count > 0:
    #         responses = response.responses
    #         failed_tokens = []
    #         for idx, resp in enumerate(responses):
    #             if not resp.success:
    #                 # The order of responses corresponds to the order of the registration tokens.
    #                 failed_tokens.append(registration_tokens[idx])
    #         print('List of tokens that caused failures: {0}'.format(failed_tokens))

    @action(methods=['PUT'], detail=False, url_path='subscribers_message')
    def subscribers_message(self, request):
        # The topic name can be optionally prefixed with "/topics/".
        data = request.data
        topic = data.get('topic')

        # See documentation on defining a message payload.
        message = messaging.Message(
            notification=messaging.Notification(
                title='안녕하세요 이 메세지를 본다면',
                body='{0}을/를 구독한 닝긴이십니다.'.format(topic),
            ),
            data={
                'score': '850',
                'time': '2:45',
            },
            topic=topic,
        )

        # Send a message to the devices subscribed to the provided topic.
        ret = {}
        response = messaging.send(message)
        # Response is a message ID string.
        ret['message'] = "Successfully sent message"
        ret['response'] = response
        return Response(ret, status=status.HTTP_200_OK)


# 주제 구독하기
# def subscription(tokens, topic):
#     response = messaging.subscribe_to_topic(tokens, topic)
#     print(response.success_count, 'tokens were subscribed successfully')
#
#
# def unsubscription(tokens, topic):
#     response = messaging.unsubscribe_from_topic(tokens, topic)
#     print(response.success_count, 'tokens were unsubscribed successfully')
