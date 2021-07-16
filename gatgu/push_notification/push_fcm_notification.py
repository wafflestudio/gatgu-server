from firebase_admin import messaging
from rest_framework import status
from rest_framework.response import Response

from push_notification.models import DeviceToken


def save_token(request):
    user = request.user
    data = request.data
    token = data.get('token')

    DeviceToken.objects.create(user=user, token=token)

    return Response({"message: Successfully saved this device"}, status=status.HTTP_201_CREATED)


def send_to_firebase_cloud_messaging(request):
    # token = '클라이언트에서 서버에 전송해 저장할 유저의 FCM 토큰'
    token = DeviceToken.objects.get(user=request.user)

    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title='안녕하세요 타이틀 입니다',
            body='안녕하세요 메세지 입니다',
        ),
        token=token,
    )

    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
