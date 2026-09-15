from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version="v1",
        description="Cookie based authentication using Django REST Framework",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        ensure_csrf_cookie(schema_view.with_ui("swagger", cache_timeout=0)),
        name="swagger",
    ),
]