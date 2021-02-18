<<<<<<< HEAD
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    joined_at = serializers.DateTimeField(read_only=True)
    userprofile = serializers.SerializerMethodField()
    user_type = serializers.ChoiceField(write_only=True, allow_null=True, required=False, choices=UserProfile.USER_TYPE)
    area = serializers.CharField(write_only=True, allow_blank=False, required=False)
    nickname = serializers.CharField(write_only=True, allow_blank=False, required=False)
    phone = serializers.CharField(write_only=True,
                                  allow_blank=False,
                                  max_length=13,
                                  required=False,
                                  validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                                             message="Phone number must be entered in the format '000-0000-0000'",
                                                             )
                                              ]
                                  )
    profile_pics = serializers.ImageField(write_only=True, required=False, allow_null=True, use_url=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'user_type',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'joined_at',
            'userprofile',
            'area',
            'nickname',
            'phone',
            'profile_pics',
        )

    def get_userprofile(self, user):
        return UserProfileSerializer(user.userprofile,
                                     context=self.context).data

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if bool(first_name) ^ bool(last_name):
            api_exception = serializers.ValidationError("First name and last name should appear together.")
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            api_exception = serializers.ValidationError("First name or last name should not have number.")
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception

        # profile_serializer = UserProfileSerializer(data=data, context=self.context)
        # profile_serializer.is_valid(raise_exception=True)

        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('area', '')
        validated_data.pop('nickname', '')
        validated_data.pop('phone', '')
        validated_data.pop('user_type', None)
        validated_data.pop('profile_pics', None)
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        return user

    def update(self, user, validated_data):
        area = validated_data.get('area')
        nickname = validated_data.get('nickname')
        phone = validated_data.get('phone')
        profile_pics = validated_data.get('profile_pics')

        # user_type = validated_data.pop('user_type', '')

        profile = user.userprofile
        if area is not None:
            profile.area = area
        if nickname is not None:
            profile.nickname = nickname
        if phone is not None:
            profile.phone = phone
        if profile_pics is not None:
            profile.profile_pics = profile_pics
        #        if user_type is not None:
        #            profile.user_type = user_type
        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_type',
            'area',
            'nickname',
            'phone',
            'profile_pics',
        ]
||||||| 78d8143
=======
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from user.models import UserProfile
import datetime


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    userprofile = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    address = serializers.CharField(
        write_only=True, allow_blank=False, required=False)
    nickname = serializers.CharField(
        write_only=True, allow_blank=False, required=False)
    phone = serializers.CharField(
        write_only=True,
        allow_blank=False,
        max_length=13,
        required=False,
    )
    picture = serializers.ImageField(
        write_only=True, required=False, allow_null=True, use_url=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'userprofile',
            'is_active',
            'address',
            'nickname',
            'phone',
            'picture',
        )

    def get_userprofile(self, user):
        return UserProfileSerializer(user.userprofile,
                                     context=self.context).data

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if bool(first_name) ^ bool(last_name):
            message = "First name and last name should appear together."
            api_exception = serializers.ValidationError(message)
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            message = "First name or last name should not have number."
            api_exception = serializers.ValidationError(message)
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('address', '')
        validated_data.pop('nickname', '')
        validated_data.pop('phone', '')
        validated_data.pop('picture', None)
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        return user

    def update(self, user, validated_data):

        address = validated_data.get('address')
        nickname = validated_data.get('nickname')
        phone = validated_data.get('phone')
        picture = validated_data.get('picture')

        profile = user.userprofile
        if address is not None:
            profile.address = address
        if nickname is not None:
            profile.nickname = nickname
        if phone is not None:
            profile.phone = phone
        if picture is not None:
            profile.picture = picture

        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    address = serializers.CharField(allow_blank=False, required=False)
    nickname = serializers.CharField(allow_blank=False, required=False)
    phone = serializers.CharField(
        allow_blank=False,
        max_length=13,
        required=False,
    )
    is_snu = serializers.BooleanField(read_only=True, default=False)
    updated_at = serializers.DateTimeField(read_only=True)
    withdrew_at = serializers.DateTimeField(read_only=True, allow_null=True)
    picture = serializers.ImageField(
        required=False, allow_null=True, use_url=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'address',
            'nickname',
            'phone',
            'is_snu',
            'updated_at',
            'withdrew_at',
            'picture',
        ]
>>>>>>> 9a699bd6ac283118129a8de9d6ba65fc1b3cc756
