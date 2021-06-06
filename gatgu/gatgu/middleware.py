from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.exceptions import InvalidToken


class GatguExceptionHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        print(exception)
        if type(exception) is InvalidToken:
            return JsonResponse({'error_code': 103, 'detail': 'Token is invalid or expired'})
        if issubclass(type(exception), APIException):
            data = {'error_code': exception.detail.code, 'detail': exception.detail}
            return JsonResponse(data)
        else:
            return JsonResponse({'error_code': 999, 'detail': 'unknown_error'})
