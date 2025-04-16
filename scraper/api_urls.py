from django.urls import path

from . import api_views

app_name='scraper_api'

urlpatterns = [
    path('search_and_download/', api_views.search_and_get_links, name='search_and_download'),
]

