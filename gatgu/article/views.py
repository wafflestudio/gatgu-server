from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from article.models import Article
from article.serializers import ArticleSerializer


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        return self.permission_classes

    @transaction.atomic
    def create(self, request):
        need_type = self.request.query_params.get('need')

        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=user, need_type=need_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        title = self.request.query_params.get('title')
        articles = self.get_queryset() if not title else self.get_queryset().filter(title__icontains=title)

        data = ArticleSerializer(articles, many=True).data
        return Response(data, status=status.HTTP_200_OK)