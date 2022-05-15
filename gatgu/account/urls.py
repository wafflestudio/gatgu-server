from django.urls import path, include
from rest_framework.routers import SimpleRouter
from account.views.base_views import UserViewSet
from account.views.kakao_views import KakaoSignInAPIView, KakaoSignInCallBackAPIView

app_name = "account"
router = SimpleRouter()
router.register("account", UserViewSet, basename="account")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "account/kakao/signin/",
        KakaoSignInAPIView.as_view(),
        name="kakao-sign-in",
    ),
    path(
        "account/kakao/signin/callback/",
        KakaoSignInCallBackAPIView.as_view(),
        name="kakao-sign-in-call-back",
    ),
]
