from django.core.cache import caches
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from article.models import Article
from article.serializers import ArticleSerializer
from user.serializers import UserSerializer, UserProfileSerializer
from .models import User, UserProfile
from .makecode import generate_code
import requests


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('create', 'login', 'confirm', 'reconfirm', 'activate'):
            return (AllowAny(),)
        return self.permission_classes

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

            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)

        response_data = {"error": "아이디나 패스워드가 잘못 됐습니다."}
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['PUT'])  # 로그아웃
    def logout(self, request):
        logout(request)
        return Response({"message": "성공적으로 로그아웃 됐습니다."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path='confirm', url_name='confirm')
    def confirm(self, request):

        email = request.data.get("email")

        if EmailProfile.objects.filter(email=email, is_pending=True).exists():
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

        ncache.set(email, confirm_number+1, timeout=1200)

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
        ecache.set(email, 1, timeout=600)

        response_data = {"message": "성공적으로 인증하였습니다."}
        return Response(response_data, status=status.HTTP_200_OK)

    # Get /user/{user_id} # 유저 정보 가져오기(나 & 남)
    def retrieve(self, request, pk=None):

        if pk == 'me':
            user = request.user
        else:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                response_data = {"message": "해당하는 회원이 없습니다."}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser:

            if not user.is_active or user.is_superuser:
                response_data = {
                    "message": "다른 회원의 정보를 볼 수 없습니다."}
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)
            else:
                pass
        else:
            pass

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    def list(self, request):

        if request.user.is_superuser:
            users = User.objects.all()
        else:
            users = User.objects.filter(is_active=True, is_superuser=False)

        return Response(self.get_serializer(users, many=True).data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=['GET'], url_path='activity')
    def hosted_list(self, request, pk):
        user_tar = self.get_object()
        if user_tar.is_active:
            hosted = Article.objects.filter(
                deleted_at=None, writer=user_tar).all()
            if hosted:
                data = ArticleSerializer(hosted, many=True).data
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(' message : 해당 글이 없습니다. ', status=status.HTTP_404_NOT_FOUND)
        else:
            return Response('message : 탈퇴한 회원입니다. ', status=status.HTTP_404_NOT_FOUND)
