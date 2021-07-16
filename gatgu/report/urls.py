from django.urls import path, include
from rest_framework.routers import SimpleRouter
from report.views import ReportViewSet

router = SimpleRouter()
router.register('reports', ReportViewSet, basename='reports')


urlpatterns = [
    path('', include((router.urls)))
]