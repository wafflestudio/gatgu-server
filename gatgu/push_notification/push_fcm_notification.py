from firebase_admin import messaging


def send_to_firebase_cloud_messaging(token):
    # This registration token comes from the client FCM SDKs.
    # token = '클라이언트에서 서버에 전송해 저장할 유저의 FCM 토큰'

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
