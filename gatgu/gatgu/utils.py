import datetime
from math import floor

from django.http import JsonResponse
from rest_framework import status, serializers
from rest_framework.exceptions import APIException, ValidationError, NotAuthenticated
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


def custom_exception_handler(exc: APIException, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the customed error code and detail to the response.
    if response is not None:
        # if type(exc) is InvalidToken:
        if isinstance(exc, InvalidToken):
            return JsonResponse(
                {
                    'detail': '다시 로그인 해주세요.',
                    'error_code': 101
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 탈퇴한 회원의 access token으로 활동 시
        # elif type(exc) is AuthenticationFailed or type(exc) is NotAuthenticated:
        elif isinstance(exc, AuthenticationFailed) or isinstance(exc, NotAuthenticated):
            return JsonResponse(
                {
                    "detail": "로그인이 필요합니다.",
                    "error_code": 100
                }
                , status=status.HTTP_401_UNAUTHORIZED
            )

        elif isinstance(exc, ValidationError):
            # print(exc.detail)
            # response.data['error_code'] = 400

            if 'username' in exc.detail:
                if hasattr(exc.detail, 'username'):
                    return JsonResponse(
                        {
                            'detail': "이미 사용중인 아이디 입니다.",
                            'error_code': 105
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            print(exc.detail)

        # elif type(exc) is rest_framework.exceptions.MethodNotAllowed:
        #     return JsonResponse(
        #         {
        #             'detail': "요청 방식이 올바르지 않습니다.",
        #             'error_code': 300
        #         },
        #         status=status.HTTP_405_METHOD_NOT_ALLOWED
        #     )
        # elif type(exc) is django.http:
        #     response.data['detail'] = 'Rdaf'
        else:
            print(type(exc))
            if not hasattr(exc, 'default_code'):
                return JsonResponse(
                    {
                        'detail': "알 수 없는 에러가 발생했습니다.",
                        'error_code': 500
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR

                )
            response.data['error_code'] = exc.default_code

    return response


# Email Acvicate

class MailActivateDone(APIException):
    status_code = 400
    default_detail = '이미 인증된 이메일 입니다. 회원가입을 진행해 주세요.'
    default_code = 102


class MailActivateFailed(APIException):
    status_code = 400
    default_detail = '인증되지 않은 이메일입니다.'
    default_code = 103


class CodeNotMatch(APIException):
    status_code = 400
    default_detail = '인증 코드가 일치하지 않습니다.'
    default_code = 104


class UsedNickname(APIException):
    status_code = 400
    default_detail = '이미 사용중인 닉네임 입니다.'
    default_code = 104


class FieldsNotFilled(APIException):
    status_code = 400
    default_detail = '필수 입력 항목이 누락되었습니다.'
    default_code = 201


class UserInfoNotMatch(APIException):
    status_code = 400
    default_detail = '아이디나 비밀번호를 확인해 주세요.'
    default_code = 106


class UserNotFound(APIException):
    status_code = 404
    default_detail = '해당 회원을 찾을 수 없습니다.'
    default_code = 107


class NotPermitted(APIException):
    status_code = 403
    default_detail = '권한이 없습니다.'
    default_code = 108


class NotEditableFields(APIException):
    status_code = 400
    default_detail = '수정할 수 없는 항목이 포함된 요청입니다.'
    default_code = 109


class ArticleNotFound(APIException):
    status_code = 404
    default_detail = '해당 게시글을 찾을 수 없습니다.'
    default_code = 121


class QueryParamsNOTMATCH(APIException):
    status_code = 400
    default_detail = '검색 조건이 올바르지 않습니다.'
    default_code = 122


class BadRequestException(APIException):
    def __init__(self, string):
        self.default_detail = f'{string}'
        super(BadRequestException, self).__init__()

    status_code = 400
    default_code = 'badrequest'


class JSTimestampField(serializers.Field):
    def to_representation(self, value):
        return floor(value.timestamp() * 1000)


from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
import pytz

KST = datetime.timezone(datetime.timedelta(hours=9))


class TimeManager:
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    WEEKDAY = ('월', '화', '수', '목', '금', '토', '일')

    @classmethod
    def today(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST)
        today = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            today = today + datetime.timedelta(days=1)
        return today

    @classmethod
    def tomorrow(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST) + datetime.timedelta(days=1)
        tomorrow = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            tomorrow = tomorrow + datetime.timedelta(days=1)
        return tomorrow

    @classmethod
    def yesterday(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST) - datetime.timedelta(days=1)
        yesterday = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        now = _from
        datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, tzinfo=KST)
        if end:
            yesterday = yesterday + datetime.timedelta(days=1)
        return yesterday

    @classmethod
    def this_monday(cls, _from: datetime = None, end=False):
        today = cls.today(_from=_from, end=end)
        return today - datetime.timedelta(days=today.weekday())

    @classmethod
    def this_month(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = cls.today()
        this_month = datetime.datetime(year=_from.year, month=_from.month, day=1, tzinfo=KST)
        if end:
            this_month += relativedelta(months=1)
        return this_month

    @classmethod
    def before_monday(cls, _from: datetime = None, end=False):
        this_monday = cls.this_monday(_from=_from, end=end)
        return this_monday - datetime.timedelta(days=7)

    @classmethod
    def this_friday(cls, end=False):
        today = cls.today(end=end)
        return today - datetime.timedelta(days=today.weekday() - 4)

    @classmethod
    def this_sunday(cls, end=False):
        today = cls.today(end=end)
        return today - datetime.timedelta(days=today.weekday() - 6)

    @classmethod
    def before_sunday(cls, end=False):
        this_sunday = cls.this_sunday(end=end)
        return this_sunday - datetime.timedelta(days=7)

    @classmethod
    def now(cls):
        return timezone.localtime(timezone=KST)

    @classmethod
    def day_before_in_business_day(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST)
        today = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            today = today + datetime.timedelta(days=1)
        if today.weekday() == cls.MONDAY:
            return today - datetime.timedelta(days=3)
        else:
            return today - datetime.timedelta(days=1)

    @classmethod
    def get_kst_time_from_timestamp(cls, timestamp: int) -> datetime:
        return datetime.datetime.fromtimestamp(timestamp, KST)