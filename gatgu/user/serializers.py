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
    phonenumber = serializers.CharField(
        write_only=True,
        allow_blank=False,
        max_length=13,
        required=False,
        validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                   message="Phone number must be entered in the format '000-0000-0000'",
                                   )
                    ]
    )
    picture = serializers.ImageField(
        write_only=True, required=False, allow_null=True, use_url=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'userprofile',
            'is_active',
            'address',
            'nickname',
            'phonenumber',
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
        validated_data.pop('phonenumber', '')
        validated_data.pop('picture', None)
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        return user

    def update(self, user, validated_data):

        address = validated_data.get('address')
        nickname = validated_data.get('nickname')
        phonenumber = validated_data.get('phonenumber')
        picture = validated_data.get('picture')

        profile = user.userprofile
        if address is not None:
            profile.address = address
        if nickname is not None:
            profile.nickname = nickname
        if phonenumber is not None:
            profile.phonenumber = phonenumber
        if picture is not None:
            profile.picture = picture

        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    address = serializers.CharField(allow_blank=False, required=False)
    nickname = serializers.CharField(allow_blank=False, required=False)
    phonenumber = serializers.CharField(
        allow_blank=False,
        max_length=13,
        required=False,
        validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                   message="Phone number must be entered in the format '000-0000-0000'",
                                   )
                    ]
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
            'phonenumber',
            'is_snu',
            'updated_at',
            'withdrew_at',
            'picture',
        ]
