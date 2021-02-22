from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
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

        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    '''superuser인 경우 삭제된 글 열람 가능'''
    def list(self, request):
        title = self.request.query_params.get('title')
        if request.user.is_superuser:
            articles = self.get_queryset() if not title else self.get_queryset().filter(
                title__icontains=title)
        else:
            articles = self.get_queryset().filter(deleted_at=None) if not title else self.get_queryset().filter(
                title__icontains=title,
                deleted_at=None)

        data = ArticleSerializer(articles, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.deleted_at:
            return Response("message:this article is deleted",status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(article).data)

    def update(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.writer:
            return Response({"error": "Can't update other User's article"}, status=status.HTTP_403_FORBIDDEN)

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
        return Response({"successfully deleted this article."}, status=status.HTTP_200_OK)
