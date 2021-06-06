from sqlite3 import IntegrityError

import rest_framework
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError, NotAuthenticated
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


def custom_exception_handler(exc: APIException, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the customed error code and detail to the response.
    if response is not None:
        if type(exc) is InvalidToken:
            return JsonResponse(
                {
                    'detail': '다시 로그인 해주세요.',
                    'error_code': 101
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 탈퇴한 회원의 access token으로 활동 시
        elif type(exc) is AuthenticationFailed or type(exc) is NotAuthenticated:
            return JsonResponse(
                {
                    "detail": "로그인이 필요합니다.",
                    "error_code": 100
                }
                , status=status.HTTP_401_UNAUTHORIZED
            )

        elif type(exc) is ValidationError:
            if 'username' in exc.detail:
                return JsonResponse(
                    {
                        # 'detail': exc.detail,
                        'detail': "이미 사용중인 아이디 입니다.",
                        'error_code': 105
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif type(exc) is rest_framework.exceptions.MethodNotAllowed:
            return JsonResponse(
                {
                    'detail': "요청 방식이 올바르지 않습니다.",
                    'error_code': 300
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        else:
            print(type(exc))
            # response.data['detail'] = '올바른 요청이 아닙니다.'
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
    default_detail = '해당 회원을 찾을 수 없읍니다.'
    default_code = 107

class NotPermitted(APIException):
    status_code = 403
    default_detail = '권한이 없습니다.'
    default_code = 108

class NotWritableFields(APIException):
    status_code = 400
    default_detail = '수정할 수 없는 항목이 포함된 요청입니다.'
    default_code = 109


