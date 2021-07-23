from django.urls import path, include
from rest_framework.routers import SimpleRouter
from push_notification.views import FCMViewSet

router = SimpleRouter()
router.register('fcm', FCMViewSet, basename='fcm')

urlpatterns = [
    path('', include((router.urls)))
]
