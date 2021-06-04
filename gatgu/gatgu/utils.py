from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the customed error code and detail to the response.
    if response is not None:
        # response.data.pop('detail') if response.data('detail') else None
        print(response.data)
        # response.data['error_code'] = exc.detail.code
        response.data['detail'] = exc.detail

    return response


class DamnError(APIException):
    status_code = 400
    default_detail = 'Dammnn'
    default_code = '99'
