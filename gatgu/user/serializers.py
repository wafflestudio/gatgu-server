from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(required=True)
    # password = serializers.CharField(required=True, write_only=True)
    # email = serializers.EmailField(required=True)
    # first_name = serializers.CharField(required=False)
    # last_name = serializers.CharField(required=False)
    # last_login = serializers.DateTimeField(read_only=True)
    # date_joined = serializers.DateTimeField(read_only=True)

    userprofile = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)
    nickname = serializers.CharField(
        write_only=True,
        allow_blank=True,
        max_length=20,
        required=False,
    )
    picture = serializers.ImageField(
        write_only=True,
        allow_null=True,
        use_url=True,
        required=False,
    )
    trading_address = serializers.CharField(write_only=True,
                                          allow_null=True,
                                          required=False,
                                          )
    grade = serializers.IntegerField(write_only=True,
                                     allow_null=True,
                                     required=False
                                     )
    point = serializers.IntegerField(write_only=True,
                                     allow_null=True,
                                     required=False
                                     )

    participated_count = serializers.SerializerMethodField()
    hosted_count = serializers.SerializerMethodField()

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
            'trading_address',
            'grade',
            'point',

            'participated_count',
            'hosted_count',

        )

    def get_participated_count(self, user):
        part_cnt = user.participant_profile.count()
        return part_cnt

    def get_hosted_count(self, user):
        hst_cnt = user.article.count()
        return hst_cnt

    def get_userprofile(self, user):
        try:
            return UserProfileSerializer(user.userprofile,
                                         context=self.context).data
        except ObjectDoesNotExist:

            message = "Cannot find your profile."
            api_exception = serializers.ValidationError(message)
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        return data

    @transaction.atomic
    def create(self, validated_data):
        nickname = validated_data.pop('nickname', '')
        picture = validated_data.pop('picture', None)
        trading_address = validated_data.pop('trading_address', '')

        user = super(UserSerializer, self).create(validated_data)

        UserProfile.objects.create(user_id=user.id,
                                   nickname=nickname,
                                   picture=picture,
                                   trading_address=trading_address,
                                   )

        return user

    def update(self, user, validated_data):

        nickname = validated_data.get('nickname')
        picture = validated_data.get('picture')
        trading_address = validated_data.get('trading_address')

        profile = user.userprofile

        if nickname:
            profile.nickname = nickname
        if picture:
            profile.picture = picture
        if trading_address:
            profile.trading_address = trading_address

        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'nickname',
            'picture',
            'updated_at',
            'withdrew_at',
            'trading_address',
            'grade',
            'point',
        )


class SimpleParticipantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = (
            'user_id',
            'nickname',
            'picture',
        )


class SimpleUserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()
    participated_count = serializers.SerializerMethodField()
    hosted_count = serializers.SerializerMethodField()
    trading_address = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'nickname',
            'picture',
            'trading_address',
            'grade',
            'participated_count',
            'hosted_count',
        )

    def get_nickname(self, user):
        return user.userprofile.nickname

    def get_picture(self, user):
        return user.userprofile.picture

    def get_trading_address(self, user):
        return user.userprofile.trading_address

    def get_grade(self, user):
        return user.userprofile.grade

    def get_participated_count(self, user):
        part_cnt = user.participant_profile.count()
        return part_cnt

    def get_hosted_count(self, user):
        hst_cnt = user.article.count()
        return hst_cnt


#
class TokenResponseSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, user):
        refresh = TokenObtainPairSerializer.get_token(user)
        data = dict()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data
