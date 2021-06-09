import boto3
from botocore.config import Config
from django.core.cache import caches
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.core.mail import EmailMessage
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView

from article.models import Article
from article.serializers import SimpleArticleSerializer
from chat.serializers import SimpleOrderChatSerializer
from chat.views import OrderChatViewSet
from gatgu.paginations import CursorSetPagination, UserActivityPagination, OrderChatPagination
from gatgu.utils import MailActivateFailed, MailActivateDone, CodeNotMatch, FieldsNotFilled, UsedNickname, \
    UserInfoNotMatch, UserNotFound, NotPermitted, NotWritableFields

from user.serializers import UserSerializer, UserProfileSerializer, SimpleUserSerializer, TokenResponseSerializer
from .models import User, UserProfile
from .makecode import generate_code


class CursorSetPagination(CursorSetPagination):
    ordering = '-date_joined'


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)
    authentication_classes = (JWTAuthentication,)

    def get_pagination_class(self):
        if self.action == 'retrieve':
            if self.request.query_params.get('activity') in ('hosted', 'participated'):
                return UserActivityPagination
            if self.request.query_params.get('activity') == 'chats':
                return OrderChatPagination
        return CursorSetPagination

    pagination_class = property(fget=get_pagination_class)

    def get_permissions(self):
        if self.action in (
                'create', 'login', 'confirm', 'reconfirm', 'activate', 'list') or self.request.user.is_superuser:
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self, pk=None):
        if self.action == 'list':
            if self.request.user.is_superuser:
                return UserSerializer
            return SimpleUserSerializer
        if self.action == 'retrieve' and pk != 'me':
            return SimpleUserSerializer

        return UserSerializer

    def get_message(self, code):

        message = "인증번호입니다.\n\n인증번호 : " + code

        return message

    def send_mail(self, email_address, code):

        message = self.get_message(code)

        mail_subject = "[gatgu] 회원가입 인증 메일입니다."
        user_email = email_address
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()

        return

    # POST /user/ 회원가입
    @transaction.atomic
    def create(self, request):

        data = request.data

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        trading_address = data.get('trading_address')

        if not username or not password or not email or not trading_address:
            raise FieldsNotFilled

        # ecache = caches["activated_email"]
        # chk_email = ecache.get(email)
        #
        # if chk_email is None:
        #     raise MailActivateFailed

        nickname = data.get('nickname')

        if UserProfile.objects.filter(nickname__iexact=nickname,
                                      withdrew_at__isnull=True).exists():  # only active user couldn't conflict.
            raise UsedNickname

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        userprofile_serializer = UserProfileSerializer(data=data)
        userprofile_serializer.is_valid(raise_exception=True)

        # try:
        user = serializer.save()
        # except IntegrityError:
        #     raise Exception()

        login(request, user)

        # ecache.set(email, 0, timeout=0)

        data = TokenResponseSerializer(user).data
        data["message"] = "성공적으로 회원가입 되었습니다."

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /user/login/  로그인
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise FieldsNotFilled

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            return Response(TokenResponseSerializer(user).data)

        raise UserInfoNotMatch

    @action(detail=False, methods=['PUT'])  # 로그아웃
    def logout(self, request):
        logout(request)
        return Response({"message": "성공적으로 로그아웃 됐습니다."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path='confirm', url_name='confirm')
    def confirm(self, request):

        email = request.data.get("email")

        ecache = caches["activated_email"]
        chk_email = ecache.get(email)

        if chk_email is not None:
            raise MailActivateDone

        ncache = caches["number_of_confirm"]

        confirm_number = ncache.get(email)

        if confirm_number is None:
            confirm_number = 0

        if confirm_number >= 10:
            response_data = {"error": "너무 많이 인증요청을 하셨습니다. 2시간 후에 다시 시도해주십시오."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        code = generate_code()

        cache = caches["email"]

        cache.set(email, code, timeout=300)

        ncache.set(email, confirm_number + 1, timeout=1200)

        self.send_mail(email, code)

        return Response({"message": "성공적으로 인증 메일을 발송하였습니다."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path='activate', url_name='activate')
    def activate(self, request):

        email = request.data.get("email")
        code = request.data.get("code")

        cache = caches["email"]
        ncache = caches["number_of_confirm"]

        email_code = cache.get(email)

        if email_code is None:
            raise MailActivateFailed

        if email_code != code:
            raise CodeNotMatch

        ecache = caches["activated_email"]

        cache.set(email, code, timeout=0)  # erase from cache
        ncache.set(email, 0, timeout=0)
        ecache.set(email, 1, timeout=10800)

        response_data = {"message": "성공적으로 인증하였습니다."}
        return Response(response_data, status=status.HTTP_200_OK)

    # Get /user/{user_id} # 유저 정보 가져오기(나 & 남)
    def retrieve(self, request, pk=None):

        qp = self.request.query_params.get('activity')

        # pk == me 인 경우 요청을 보낸 유저의 정보 찾기, 그 이외의 pk 인 경우 타겟유저를 조회
        user = self.request.user if pk == 'me' else self.get_object()

        # if not user or not user.is_active:
        #     return Response("message: 해당 유저를 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

        # return user's article list
        if qp:
            # 관리자모드에서만 지워진 글 확인
            queryset = Article.objects.all() if user.is_superuser else Article.objects.filter(deleted_at=None)

            if qp == 'hosted':
                articles = queryset.filter(writer=user, deleted_at=None)
                if not articles:
                    return Response("호스트한 같구가 없습니다.", status=status.HTTP_404_NOT_FOUND)

                page = self.paginate_queryset(articles)
                assert page is not None
                serializer = SimpleArticleSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            elif qp == 'participated':
                articles = queryset.filter(order_chat__participant_profile__participant=user)
                if not articles:
                    return Response("참여한 같구가 없습니다.", status=status.HTTP_404_NOT_FOUND)

                page = self.paginate_queryset(articles)
                assert page is not None
                serializer = SimpleArticleSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # show chat list that 'me' in if not superuser
            elif qp == 'chats':

                # 관리자 모드인 경우에만 다른 유저의 채팅 리스트 조회 가능
                if pk == 'me':
                    user = request.user
                else:
                    user = self.get_object()
                    if not user.is_superuser:
                        return Response("message: 다른회원의 채팅리스트를 열람할 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

                chats = OrderChatViewSet.queryset.filter(
                    Q(participant_profile__participant=user) | Q(article__writer=user))
                # chats = OrderChatViewSet.queryset.filter(participant_profile__participant=user)
                # chats = OrderChatViewSet.queryset.filter(article__writer=user)

                # chats = OrderChatViewSet.queryset.filter(participant_profile__participant_id=user.id) |
                # OrderChatViewSet.queryset.filter(participant_profile__participant_id=user.id)

                if not chats:
                    return Response("참여중인 채팅이 없습니다.", status=status.HTTP_404_NOT_FOUND)
                page = self.paginate_queryset(chats)
                assert page is not None
                serializer = SimpleOrderChatSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

                # serializer = SimpleOrderChatSerializer(chats, many=True)
                # return Response(serializer.data, status=status.HTTP_200_OK)

        # return user detail
        else:

            if pk == 'me':
                user = request.user
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            else:
                user = self.get_object()
                if user:
                    serializer = self.get_serializer(user)
                    if not user.is_active:
                        raise UserNotFound
                        # return Response({'message : 탈퇴한 회원입니다.'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    raise UserNotFound
                    # return Response({'message: 해당하는 회원이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

                return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):

        if request.user.is_superuser:
            users = self.get_queryset()
        else:
            users = self.get_queryset().filter(is_active=True, is_superuser=False)

        page = self.paginate_queryset(users)
        assert page is not None
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    # 회원탈퇴
    @action(detail=False, methods=['PUT'], url_path='withdrawal', url_name='withdrawal')
    def withdrawal(self, request):

        user = request.user

        if user.is_active:
            profile = user.userprofile
            profile.withdrew_at = timezone.now()
            profile.save()
            user.is_active = False
            user.save()
        else:
            response_data = {"error": "이미 탈퇴한 회원입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "성공적으로 탈퇴 하였습니다."}, status=status.HTTP_200_OK)

    # PUT /user/me/  # 유저 정보 수정 (나)
    @transaction.atomic
    @action(detail=True, methods=['PATCH'], url_path='edit')
    def update_me(self, request, pk=None):

        if pk != 'me':
            raise NotPermitted
            # response_data = {"error": "다른 회원의 정보를 수정할 수 없습니다."}
            # return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        data = request.data

        cnt = 0

        # 유저 아이디 수정 불가로 변경
        for key in ['nickname', 'picture', 'password', 'trading_address']:
            if key in data:
                cnt += 1

        if cnt != len(data):
            raise NotWritableFields

        nickname = data.get('nickname')

        if UserProfile.objects.filter(nickname__iexact=nickname,
                                      withdrew_at__isnull=True).exclude(user_id=user.id).exists():
            raise UsedNickname

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['PUT'])
    def get_presigned_url(self, request):
        user = request.user
        data = request.data
        if data['method'] == 'get' or data['method'] == 'GET':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': data['file_name']
                },
                ExpiresIn=3600,
                HttpMethod='GET')
            return Response({'presigned_url': url, 'file_name': data['file_name']}, status=status.HTTP_200_OK)
        elif data['method'] == 'put' or data['method'] == 'PUT':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': 'user/{0}/{1}_{2}'.format(user.id, data['file_name'], user.id)
                },
                ExpiresIn=3600,
                HttpMethod='PUT')
            return Response(
                {'presigned_url': url, 'file_name': 'user/{0}/{1}_{2}'.format(user.id, data['file_name'], user.id)},
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

