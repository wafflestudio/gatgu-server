from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from article.models import Article
from gatgu.utils import UserNotFound, BadRequestException, ArticleNotFound
from report.models import Report
from report.serializers import ReportSerializer


class ReportViewSet(viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    authentication_classes = (JWTAuthentication,)

    @transaction.atomic
    def create(self, request):
        data = request.data
        target_user_id = data.get('target_user_id')
        article_id = data.get('article_id')
        contents = data.get('contents')

        if (target_user_id and article_id) or (not target_user_id and not article_id):
            raise BadRequestException('(target_user_id) or (article_id) only one permitted')

        if target_user_id:
            try:
                target_user = User.objects.get(id=target_user_id)
                report = Report.objects.create(reporter=self.request.user, target_user=target_user, contents=contents)
            except User.DoesNotExist:
                raise UserNotFound()
        elif article_id:
            try:
                article = Article.objects.get(id=article_id)
                report = Report.objects.create(reporter=self.request.user, article=article, contents=contents)
            except Article.DoesNotExist:
                raise ArticleNotFound()

        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
