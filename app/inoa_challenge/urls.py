from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

from .routers import router

urlpatterns = [
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api-token-auth/", views.obtain_auth_token),
]
