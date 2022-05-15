from django.urls import path, include
from rest_framework.routers import SimpleRouter
from account.views import UserViewSet

app_name = "account"
router = SimpleRouter()
router.register("account", UserViewSet, basename="account")

urlpatterns = [path("", include(router.urls))]
