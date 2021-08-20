import datetime
import logging

import boto3
import pytz
import requests
from botocore.config import Config
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Prefetch, Subquery, OuterRef, Count, IntegerField, Sum, F, Exists
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from article.models import Article, ArticleImage
from article.serializers import ArticleSerializer, SimpleArticleSerializer, ArticleImageSerializer, \
    ArticleRetrieveSerializer
from gatgu.paginations import CursorSetPagination
from gatgu.settings import BUCKET_NAME
from gatgu.utils import FieldsNotFilled, QueryParamsNOTMATCH, ArticleNotFound, NotPermitted, NotEditableFields, \
    TimeManager

from chat.models import ParticipantProfile

from chat.models import OrderChat
from user.views import upload_s3


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
            rtn['article_status__in'] = query_params.getlist('status')
        return rtn

    @transaction.atomic
    def create(self, request):

        user = request.user
        data = request.data

        title = data.get('title')
        description = data.get('description')
        trading_place = data.get('trading_place')
        product_url = data.get('product_url')
        time_in = datetime.datetime.fromtimestamp(float(data.get('time_in') / 1000))

        if not title or not description or not trading_place or not product_url:
            raise FieldsNotFilled

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=user, time_in=time_in)

        article_id = Article.objects.last().id
        article = Article.objects.prefetch_related(self.order_chat).get(id=article_id)

        return Response(self.get_serializer(article).data, status=status.HTTP_201_CREATED)
        # return Response({"message: Article successfully posted."}, status=status.HTTP_201_CREATED)

    def list(self, request):
        filter_kwargs = self.get_query_params(self.request.query_params)
        articles = self.get_queryset().filter(**filter_kwargs)

        if not request.user.is_superuser:
            articles = articles.filter(deleted_at=None)

        articles = articles.prefetch_related(self.order_chat)

        ## cache test
        # cache_key = 'article_list'
        # c_data = cache.get('article_list')
        # if c_data is None:
        #
        #     c_data = self.get_serializer(articles, many=True).data
        #     cache.set(cache_key, c_data, timeout=10)
        #     return Response({"cache miss"}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({"cache hit"}, status=status.HTTP_200_OK)

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

        return Response(ArticleRetrieveSerializer(article).data)

    @action(detail=False, methods=['PATCH'], url_path='status')
    def article_status(self, request):
        have_activated_participant = Exists(
            ParticipantProfile.objects.filter(
                order_chat__article_id=OuterRef('id'), pay_status__gte=2)
        )
        articles = self.get_queryset()\
            .annotate(have_activated_participant=have_activated_participant)

        # 거래 진행중인 유저 있고 & 상태 모집중 -> 상태 거래중
        articles_update_to_IN_PROCESS1 = articles\
            .filter(have_activated_participant=True, article_status=Article.GATHERING) \
            .update(article_status=Article.IN_PROCESS)
        # 거래 진행중인 유저 없고 & 상태 거래중 -> 상태 모집중
        articles_update_to_GATHERING1 = articles \
            .filter(have_activated_participant=True, article_status=Article.IN_PROCESS) \
            .update(article_status=Article.GATHERING)
        # 상태 모집중 & 기간 만료된 -> 상태 만료
        articles_update_to_EXPIRED = articles \
            .filter(article_status=Article.GATHERING, time_in__lte=TimeManager.now()) \
            .update(article_status=Article.EXPIRED)
        # 거래 진행중인 유저 없고 & 기간 만료 안됬고 & 상태 만료 -> 상태 모집중
        articles_update_to_GATHERING2 = articles \
            .filter(have_activated_participant=False, time_in__gte=TimeManager.now(), article_status=Article.EXPIRED) \
            .update(article_status=Article.GATHERING)
        # 거래 진행중인 유저 있고 & 기간 만료 안됬고 & 상태 만료 -> 상태 거래중
        articles_update_to_IN_PROCESS2 = articles \
            .filter(have_activated_participant=True, time_in__gte=TimeManager.now(), article_status=Article.EXPIRED) \
            .update(article_status=Article.IN_PROCESS)

        # expired_article = articles.filter(time_in__lt=datetime.date.today())
        # if expired_article:
        #     expired_article.update(article_status=4)
        #
        # gathering_article = articles.filter(time_in__gte=datetime.date.today())
        # if gathering_article:
        #     gathering_article.update(article_status=1)

        return Response({"message": "Successfully updated the status of articles"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, pk):
        # PATCH v1/articles/{article_id}
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



        serializer = self.get_serializer(article, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'article_status' in data:
            article_status = data.get('article_status')
            serializer.save(article_status=article_status)

        if 'time_in' in data:
            time_in = datetime.datetime.fromtimestamp(float(data.get('time_in') / 1000))
            serializer.save(time_in=time_in)


        # 상태 체크 및 업데이트 api 추가
        # if article.article_status == 4 and article.time_in >= datetime.date.today():
        #     article.article_status = 1
        #     serializer.save()

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
    def create_presigned_post(self, request, pk=None):

        user = request.user
        object_key = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
        response = s3.generate_presigned_post(
            BUCKET_NAME,
            'user/{0}/article/{1}/{2}'.format(user.id, pk, object_key)
        )
        object_url = response['url'] + response['fields']['key']
        # upload_s3(response,'admin(1).jpeg')

        return Response(
            {'response': response, 'object_url': object_url}, status=status.HTTP_200_OK)
