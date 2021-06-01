from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token,verify_jwt_token,refresh_jwt_token


urlpatterns = [
    # path('admin/', admin.site.urls),

    path('api/token/', obtain_jwt_token),
    path('api/token/verify/', verify_jwt_token),
    path('api/token/refresh/', refresh_jwt_token),

    path('v1/', include('user.urls')),
    path('v1/', include('article.urls')),
    path('v1/', include('chat.urls'))

]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]