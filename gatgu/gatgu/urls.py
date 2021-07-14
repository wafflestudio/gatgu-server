from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/token/', jwt_views.token_obtain_pair),
    path('v1/token/refresh/', jwt_views.token_refresh),

    path('v1/', include('user.urls')),
    path('v1/', include('article.urls')),
    path('v1/', include('chat.urls')),


]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
