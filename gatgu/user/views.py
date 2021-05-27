from django.core.cache import caches
from django.contrib.auth import authenticate, login, logout, _get_user_session_key
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from article.models import Article
from article.serializers import ArticleSerializer, SimpleArticleSerializer
from article.views import ArticleViewSet
from chat.models import OrderChat
from chat.serializers import SimpleOrderChatSerializer
from chat.views import OrderChatViewSet
from gatgu.paginations import CursorSetPagination, UserActivityPagination, OrderChatPagination

from user.serializers import UserSerializer, UserProfileSerializer, SimpleUserSerializer
from .models import User, UserProfile
from .makecode import generate_code


class CursorSetPagination(CursorSetPagination):
    ordering = '-date_joined'


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

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
        'create', 'login', 'confirm', 'reconfirm', 'activate', 'session_flush') or self.request.user.is_superuser:
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.user.is_superuser:
                return UserSerializer
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

        if not username or not password or not email:
            response_data = {
                "error": "아이디, 비밀번호, 이메일은 필수 항목입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        ecache = caches["activated_email"]
        chk_email = ecache.get(email)

        if chk_email is None:
            response_data = {
                "error": "인증되지 않은 이메일입니다. 인증을 해주세요."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        nickname = data.get('nickname')

        if not nickname:
            response_data = {
                "error": "닉네임은 필수 항목입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if UserProfile.objects.filter(nickname__iexact=nickname,
                                      withdrew_at__isnull=True).exists():  # only active user couldn't conflict.
            response_data = {
                "error": "해당 닉네임은 사용할 수 없습니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        userprofile_serializer = UserProfileSerializer(data=data)
        userprofile_serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
        except IntegrityError:
            response_data = {
                "error": "해당 아이디는 사용할 수 없습니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        ecache.set(email, 0, timeout=0)

        data = serializer.data
        data['token'] = user.auth_token.key

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /user/login/  로그인
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            data = dict()
            token, created = Token.objects.get_or_create(user=user)
            data['message'] = "성공적으로 로그인 하였습니다."
            data['token'] = token.key
            return Response(data)

        response_data = {"error": "아이디나 패스워드가 잘못 됐습니다."}
        return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['PUT'])  # 로그아웃
    def logout(self, request):
        user = request.user
        try:
            request.session['_auth_user_id']
        except KeyError:
            return Response({"message": "로그인이 필요합니다. "}, status=status.HTTP_400_BAD_REQUEST)

        # if request.session['_auth_user_id'] != user.pk:
        #     return Response({"message": "not this id "}, status=status.HTTP_400_BAD_REQUEST)

        # if _get_user_session_key(request)
        logout(request)
        # if user is None:
        #     return Response({"message": "로그인이 필요합니다. "}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "성공적으로 로그아웃 됐습니다."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='flush')
    def session_flush(self, request):
        request.session.flush()
        return Response({"flush session"})

    @action(detail=False, methods=['PUT'], url_path='confirm', url_name='confirm')
    def confirm(self, request):

        email = request.data.get("email")

        ecache = caches["activated_email"]
        chk_email = ecache.get(email)

        if chk_email is not None:
            response_data = {"error": "이미 인증이 된 이메일입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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
            response_data = {"error": "시간이 초과되었거나, 인증 요청을 하지 않은 이메일입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if email_code != code:
            response_data = {"error": "코드가 맞지 않습니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

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

        if not user or not user.is_active:
            return Response("message: 해당 유저를 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

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
                return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
            else:
                user = self.get_object()
                if user:
                    serializer = self.get_serializer(user)
                    if not user.is_active:
                        return Response({'message : 탈퇴한 회원입니다.'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message: 해당하는 회원이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

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

    @transaction.atomic
    # PUT /user/me/  # 유저 정보 수정 (나)
    def update(self, request, pk=None):

        if pk != 'me':
            response_data = {"error": "다른 회원의 정보를 수정할 수 없습니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        data = request.data

        cnt = 0

        for key in ['nickname', 'picture', 'password']:
            if key in data:
                cnt = cnt + 1

        if cnt != len(data):
            response_data = {"error": "수정할 수 없는 정보가 있는 요청입니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        nickname = data.get('nickname')

        if UserProfile.objects.filter(nickname__iexact=nickname,
                                      withdrew_at__isnull=True).exclude(user_id=user.id).exists():
            response_data = {
                "error": "해당 닉네임은 사용할 수 없습니다."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.update(user, serializer.validated_data)

        return Response(serializer.data)
