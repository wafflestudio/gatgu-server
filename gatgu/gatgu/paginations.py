from base64 import b64encode
from urllib import parse

from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination
from rest_framework.utils.urls import replace_query_param


class CursorSetPagination(CursorPagination):
    page_size = 5
    page_size_query_param = "page_size"
    ordering = "-"

    def encode_cursor(self, cursor):

        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode('ascii')).decode('ascii')
        return replace_query_param('', self.cursor_query_param, encoded)


class UserActivityPagination(CursorPagination):
    page_size = 5
    page_size_query_param = "page_size"
    ordering = "-written_at"

    def encode_cursor(self, cursor):

        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode('ascii')).decode('ascii')
        return replace_query_param('', self.cursor_query_param, encoded)


class OrderChatPagination(CursorPagination):
    page_size = 5
    page_size_query_param = "page_size"
    ordering = "-article"

    def encode_cursor(self, cursor):

        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode('ascii')).decode('ascii')
        return replace_query_param('', self.cursor_query_param, encoded)


class GatguPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def __init__(self, page, page_size):
        self.page = str(page)
        self.page_size = str(page_size)
        super().__init__()


class GatguLimitOffsetPagination(LimitOffsetPagination):
    def __init__(self, offset, limit):
        self.offset = int(offset)
        self.default_limit = int(limit)
        super().__init__()