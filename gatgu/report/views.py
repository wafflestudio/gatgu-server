from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from gatgu.utils import UserNotFound
from report.models import Report
from report.serializers import ReportSerializer


class ReportViewSet(viewsets.GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = ()

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
        serializer.save(user=request.user, target_user=target_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
