from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
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
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
        return super(UserViewSet, self).get_permissions()

    # POST /user/ 회원가입
    def create(self, request):
        data = request.data
        usertype = request.data.get('user_type')
        if usertype == 2:
            access_token = request.POST.get('access_token', '')

            if access_token == '' or None:
                return Response({"error": "Received no access token in request"}, status=status.HTTP_400_BAD_REQUEST)

            profile_request = requests.post(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_json = profile_request.json()

            if profile_json == None:
                return Response({"error": "Received no response from Kakao database"}, status=status.HTTP_404_NOT_FOUND)

            try:  # parsing json
                kakao_account = profile_json.get("kakao_account")
                email = kakao_account.get("email", None)
                profile = kakao_account.get("profile")
                username = profile.get("nickname")
            #               profile_image = profile.get("thumbnail_image_url")
            except KeyError:
                return Response({"error": "Need to agree to terms"}, status=status.HTTP_400_BAD_REQUEST)

            if (User.objects.filter(username=username).exists()):  # 기존에 가입된 유저가 카카오 로그인
                user = User.objects.get(username=username)
                login(request, user)

                if usertype == 'django':
                    User.objects.filter(username=username).update(email=email)  ###
                    UserProfile.objects.filter(user=user).update(nickname=username, user_type='kakao')  ###

                # 위치 옮김
                data = self.get_serializer(user).data
                token, created = Token.objects.get_or_create(user=user)
                data['token'] = token.key

                return Response(data, status=status.HTTP_200_OK)
            else:  # 신규 유저의 카카오 로그인
                data = {"username": username, "email": email, "user_type": 'kakao'}  ###
        #               data['profile_image'] = profile_image

        area = request.data.get('area')
        nickname = request.data.get('nickname')
        phone = request.data.get('phone')

        if request.data.get('profile_pics') is not None:
            profile_pics = request.data.get('profile_pics')

        if UserProfile.objects.filter(nickname__iexact=nickname):
            return Response({"error": "A user with that Nickname already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if UserProfile.objects.filter(phone=phone):
            return Response({"error": "A user with that Phone Number already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.create(user_id=user.id, area=area, nickname=nickname, phone=phone,
                                                      profile_pics=profile_pics)
        except IntegrityError:
            return Response({"error": "A user with that nickname or phone number already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

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

        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['POST'])  # 로그아웃
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
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    # PUT /user/me/  # 유저 정보 수정 (나)
    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other Users information"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:

            return Response({"error": "That Nickname or Phone number is already occupied"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
