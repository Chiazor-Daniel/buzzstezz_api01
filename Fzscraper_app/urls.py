from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scraper.urls')),
    path('api/', include('scraper.api_urls')),
]
