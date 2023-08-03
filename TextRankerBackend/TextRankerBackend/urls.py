from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", include("TextRanker.urls")),
    path("kevin_sneaky_cavern/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
