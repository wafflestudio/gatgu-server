import datetime

import boto3
from botocore.config import Config
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Prefetch, Subquery, OuterRef, Count, IntegerField, Sum, F
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from article.models import Article
from article.serializers import ArticleSerializer, SimpleArticleSerializer
from gatgu.paginations import CursorSetPagination
from gatgu.utils import FieldsNotFilled, QueryParamsNOTMATCH, ArticleNotFound, NotPermitted

from chat.models import ParticipantProfile

from chat.models import OrderChat


class CursorSetPagination(CursorSetPagination):
    ordering = '-written_at'


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(),)
    authentication_classes = (JWTAuthentication,)

    pagination_class = CursorSetPagination

    # Variables for query ====================
    count_participant = Coalesce(
        Subquery(ParticipantProfile.objects.filter(order_chat_id=OuterRef('id')).values('order_chat_id')
                 .annotate(count=Count('participant_id')).values('count'),
                 output_field=IntegerField()), 0)
    sum_wish_price = Coalesce(
        Subquery(ParticipantProfile.objects.filter(order_chat_id=OuterRef('id')).values('order_chat_id')
                 .annotate(sum=Sum('wish_price')).values('sum'),
                 output_field=IntegerField()), 0)
    order_chat = Prefetch('order_chat', queryset=OrderChat.objects.annotate(count_participant=count_participant,
                                                                            sum_wish_price=sum_wish_price))

    # ====================

    def get_permissions(self):
        if self.action == 'list' or 'retrieve':
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleArticleSerializer
        return ArticleSerializer

    def get_query_params(self, query_params):

        # pagination 고려 => accept { cursor, page_size }

        # for key in query_params.keys():
        #     if key not in {'status', 'title'}:
        #         raise QueryParamsNOTMATCH
        rtn = dict()
        if 'title' in query_params:
            rtn['title__icontains'] = query_params.get('title')
        if 'status' in query_params:
            rtn['article_status'] = query_params.get('status')
        return rtn

    @transaction.atomic
    def create(self, request):

        user = request.user
        data = request.data

        title = data.get('title')
        description = data.get('description')
        trading_place = data.get('trading_place')
        product_url = data.get('product_url')
        time_in = data.get('time_in')

        if not title or not description or not trading_place or not product_url or not time_in:
            raise FieldsNotFilled

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):

        filter_kwargs = self.get_query_params(self.request.query_params)
        articles = self.get_queryset().filter(**filter_kwargs)

        # if not request.user.is_superuser:
        #     articles = articles.filter(deleted_at=None)

        articles = articles.prefetch_related(self.order_chat)

        page = self.paginate_queryset(articles)
        assert page is not None
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk):
        try:
            article = Article.objects.prefetch_related(self.order_chat).get(id=pk)
        except ObjectDoesNotExist:
            raise ArticleNotFound

        if article.deleted_at:
            raise ArticleNotFound

        return Response(self.get_serializer(article).data)

    @action(detail=False, methods=['PATCH'], url_path='status')
    def article_status(self, request):

        # 함수화 or not
        articles = self.get_queryset()
        expired_article = articles.filter(time_in__lt=datetime.date.today())
        gathering_article = articles.filter(time_in__gte=datetime.date.today())
        if expired_article and expired_article.get('article_statu') == 1:
            expired_article.update(article_status=4)
        if gathering_article:
            gathering_article.update(article_status=1)

        return Response({"message": "Successfully updated status of articles"}, status=status.HTTP_202_ACCEPTED)

    @transaction.atomic
    def partial_update(self, request, pk):
        user = request.user
        data = request.data

        try:
            article = Article.objects.prefetch_related(self.order_chat).get(id=pk)
        except ObjectDoesNotExist:
            raise ArticleNotFound

        if article.deleted_at:
            raise ArticleNotFound

        if user != article.writer:
            raise NotPermitted

        # 변경 불가 필드 에러 추가
        # if data.get['article_status'] == 2:
        #     if hasattr(data, '')

        # time_in field 변경시 오늘보다 작은 날짜 불가 하도록
        if data.get['time_in'] < datetime.date.today():
            return Response({"message": "마감일 설정이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if article.article_status == 2:
            return Response({"message": "모집완료상태의 글은 수정할 수 없습니다. "}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(article, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(article, serializer.validated_data)

        # 상태 체크 및 업데이트 api 추가
        if article.article_status == 4 and article.time_in >= datetime.date.today():
            article.article_status = 1
            serializer.save()

        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.writer:
            raise NotPermitted

        article.deleted_at = timezone.now()
        article.save()
        return Response({"message": "Successfully deleted this article."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def get_presigned_url(self, request, pk=None):
        user = request.user
        data = request.data
        if data['method'] == 'get' or data['method'] == 'GET':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': data['file_name']
                },
                ExpiresIn=3600,
                HttpMethod='GET')
            return Response({'presigned_url': url, 'file_name': data['file_name']}, status=status.HTTP_200_OK)
        elif data['method'] == 'put' or data['method'] == 'PUT':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': 'article/{0}/{1}_{2}'.format(pk, data['file_name'], user.id)
                },
                ExpiresIn=3600,
                HttpMethod='PUT')
            return Response(
                {'presigned_url': url, 'file_name': 'article/{0}/{1}_{2}'.format(pk, data['file_name'], user.id)},
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
