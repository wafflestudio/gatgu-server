from django.urls import path, include
from rest_framework.routers import SimpleRouter
from account.views import PersonViewSet

app_name = "account"
router = SimpleRouter()
router.register("account", PersonViewSet, basename="account")

urlpatterns = [path("", include(router.urls))]
