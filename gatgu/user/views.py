from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from user.serializers import UserSerializer
from .models import User, UserProfile
import requests


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
        return self.permission_classes

    # POST /user/ 회원가입
    def create(self, request):

        data = request.data

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            response_data = {
                "error": "username, password, email are required."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        address = data.get('address')
        nickname = data.get('nickname')
        phonenumber = data.get('phonenumber')

        if request.data.get('picture') is not None:
            picture = request.data.get('picture')
        else:
            picture = 'default.jpg'

        if UserProfile.objects.filter(nickname__iexact=nickname):
            response_data = {
                "error": "A user with that Nickname already exists."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if UserProfile.objects.filter(phonenumber=phonenumber):
            response_data = {
                "error": "A user with that Phone Number already exists."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # should be updated
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
            user_profile = UserProfile.objects.create(user_id=user.id,
                                                      address=address,
                                                      nickname=nickname,
                                                      phonenumber=phonenumber,
                                                      picture=picture)
        except IntegrityError:
            response_data = {
                "error": "A user with that username already exists."}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        #################

        login(request, user)

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

        response_data = {"error": "Wrong username or wrong password"}
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['PUT'])  # 로그아웃
    def logout(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

    # Get /user/{user_id} # 유저 정보 가져오기(나 & 남)
    def retrieve(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                response_data = {"message": "There is no such user."}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    def list(self, request):

        tot = request.GET.get('tot', None)

        if tot:
            if tot == "yes":
                users = User.objects.all()
            elif tot == 'no':
                users = User.objects.filter(is_active=True)
            else:
                response_data = {"message": "Invalid parameter."}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            users = User.objects.filter(is_active=True)

        return Response(self.get_serializer(users, many=True).data, status=status.HTTP_200_OK)

    # 로그아웃
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
            pass

        return Response({"message": "Successfully deactivated."}, status=status.HTTP_200_OK)

    # PUT /user/me/  # 유저 정보 수정 (나)
    def update(self, request, pk=None):

        if pk != 'me':
            response_data = {"error": "Can't update other Users information"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except IntegrityError:

            return Response({"error": "That Nickname or Phone number is already occupied"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
