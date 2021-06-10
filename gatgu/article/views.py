import boto3
from botocore.config import Config
from django.db import transaction
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
from gatgu.utils import FieldsNotFilled


class CursorSetPagination(CursorSetPagination):
    ordering = '-written_at'


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(),)
    authentication_classes = (JWTAuthentication,)

    pagination_class = CursorSetPagination

    def get_permissions(self):
        if self.action == 'list' or 'retrieve':
            return (AllowAny(),)
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleArticleSerializer
        return ArticleSerializer

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
        # title = self.request.query_params.get('title')
        # order_status = self.request.query_params.get('status')
        qp = self.request.query_params

        # 유저에게 지워지지 않은 게시물만 보여준다.
        # if request.user.is_superuser:
        #     articles = self.get_queryset() if not title else self.get_queryset().filter(
        #         title__icontains=title)
        # else:
        #     articles = self.get_queryset().filter(deleted_at=None) if not title else self.get_queryset().filter(
        #         title__icontains=title,
        #         deleted_at=None)
        if qp:
            for key in qp.keys():
                if key not in {'status', 'title'}:
                    return Response({
                        "detail": "검색 조건이 올바르지 않습니다.",
                        "error_code" : 122,
                    }, status=status.HTTP_400_BAD_REQUEST)

            if 'title' in qp and 'status' in qp:
                articles = self.get_queryset().filter(
                    title__icontains=qp.get('title'),
                    article_status=qp.get('status'),
                )
            if len(qp) == 1 and 'title' in qp:
                articles = self.get_queryset().filter(
                    title__icontains=qp.get('title'),
                )
            if len(qp) == 1 and 'status' in qp:
                articles = self.get_queryset().filter(
                    article_status=qp.get('status'),
                )
        else:
            articles = self.get_queryset()

        page = self.paginate_queryset(articles)
        assert page is not None
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.deleted_at:
            return Response(" message : This article is deleted", status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(article).data)

    @transaction.atomic
    @action(detail=True, methods=['PATCH'], url_path='edit')
    def edit(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.writer:
            return Response({"error": "다른 회원의 게시물을 수정할 수 없습니다. "}, status=status.HTTP_403_FORBIDDEN)

        # if article.article_status >= 2:
        #     return Response({"message": "모집완료상태의 글은 수정할 수 없습니다. "}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(article, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(article, serializer.validated_data)
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        if user != article.writer:
            return Response({"error": "Can't delete other User's article"}, status=status.HTTP_403_FORBIDDEN)

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
