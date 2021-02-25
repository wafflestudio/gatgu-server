from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    userprofile = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    nickname = serializers.CharField(
        write_only=True,
        allow_blank=False,
        max_length=20,
        required=False,
    )
    picture = serializers.ImageField(
        write_only=True,
        allow_null=True,
        use_url=True,
        required=False,
    )

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
            'nickname',
            'picture',
        )

    def get_userprofile(self, user):
        try:
            return UserProfileSerializer(user.userprofile,
                                         context=self.context).data
        except ObjectDoesNotExist:

            message = "Cannot find your profile."
            api_exception = serializers.ValidationError(message)
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception

            return None

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
        nickname = validated_data.pop('nickname', '')
        picture = validated_data.pop('picture', 'default.jpg')

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        UserProfile.objects.create(user_id=user.id,
                                   nickname=nickname,
                                   picture=picture)

        return user

    def update(self, user, validated_data):

        nickname = validated_data.get('nickname')
        picture = validated_data.get('picture')

        profile = user.userprofile

        if nickname:
            profile.nickname = nickname
        if picture:
            profile.picture = picture

        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(
        allow_blank=False,
        max_length=20
    )
    picture = serializers.ImageField(
        allow_null=True,
        use_url=True,
        required=False,
    )
    is_snu = serializers.BooleanField(read_only=True, default=False)
    updated_at = serializers.DateTimeField(read_only=True)
    withdrew_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'nickname',
            'picture',
            'is_snu',
            'updated_at',
            'withdrew_at',
            'picture',
