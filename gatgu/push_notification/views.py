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

        FCMToken.objects.create(fcmtoken=token)
        token_obj = FCMToken.objects.last()
        try:
            UserFCMToken.objects.create(user=user, token=token_obj)
        except IntegrityError:
            return Response({"message: you already have this token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message: This token Successfully registered"}, status=status.HTTP_201_CREATED)

    @action(methods=['PUT'], detail=False)
    def messaging(self, request):
        user = request.user

        # 희수 안드 에뮬
        token = 'caMbD4PIQC66pKoUiY-SAL:APA91bHxykMPrDy4wP2sbYvzAIIJBR5yrGsoYQsU-T7KFayyvqgvBdop7aD8W3oz00EyWdCWQ3otsu6-IDnoBUMo5pMYfzvFgJbDM0aE5juL0Ep4kkK_SINfqJa0zbsYIXJMsxKCrIor'
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
                title='안녕하세요 타이틀 입니다',
                body='안녕하세요 메세지 입니다',
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
        registration_tokens = FCMToken.objects.filter(user_fcmtoken__user=request.user).values_list('fcmtoken',
                                                                                                    flat=True)
        print(registration_tokens)

        message = messaging.MulticastMessage(
            data={'score': '850', 'time': '2:45'},
            tokens=registration_tokens,
        )

        response = messaging.send(message)

        return Response({'Successfully sent message:', response}, status=status.HTTP_200_OK)

    # @action(methods=['PUT'], detail=False, url_path='bulk_messaging')
    # def bulk_messaging(self, request):
    #     # Create a list containing up to 500 registration tokens.
    #     # These registration tokens come from the client FCM SDKs.
    #     registration_tokens = FCMToken.objects.filter(user_fcmtoken__user=request.user).values_list('fcmtoken',
    #                                                                                                 flat=True)
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

    @action(methods=['PUT'], detail=False, url_path='messaging')
    def subscribers_messaging(self, request):
        # The topic name can be optionally prefixed with "/topics/".
        topic = 'shit'

        # See documentation on defining a message payload.
        message = messaging.Message(
            data={
                'score': '850',
                'time': '2:45',
            },
            topic=topic,
        )

        # Send a message to the devices subscribed to the provided topic.
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)


def subscription(tokens, topic):
    # These registration tokens come from the client FCM SDKs.
    # registration_tokens = [
    #     'YOUR_REGISTRATION_TOKEN_1',
    #     # ...
    #     'YOUR_REGISTRATION_TOKEN_n',
    # ]
    # topic = 'shit'
    # Subscribe the devices corresponding to the registration tokens to the
    # topic.
    response = messaging.subscribe_to_topic(tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were subscribed successfully')


def unsubscription(tokens, topic):
    response = messaging.unsubscribe_from_topic(tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were unsubscribed successfully')
