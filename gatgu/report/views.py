from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from gatgu.utils import UserNotFound
from report.models import Report
from report.serializers import ReportSerializer


class ReportViewSet(viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    authentication_classes = (JWTAuthentication,)

    @transaction.atomic
    def create(self, request):
        data = request.data
        nickname = data.get('nickname')

        try:
            target_user = User.objects.get(userprofile__nickname=nickname)
        except User.DoesNotExist:
            raise UserNotFound()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter_id=request.user.id, target_user_id=target_user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
