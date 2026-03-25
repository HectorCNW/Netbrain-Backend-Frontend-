"""
NetBrain — URL principal
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/", include("apps.projects.urls")),
    path("api/", include("apps.pages.urls")),
    path("api/", include("apps.github_integration.urls")),
    path("api/", include("apps.qa.urls")),
    path("api/", include("apps.important_notes.urls")),
    path("api/", include("apps.documents.urls")),
    path("api/", include("apps.search.urls")),
    path("api/", include("apps.exports.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
