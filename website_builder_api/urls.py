# website_builder_api/urls.py

from django.urls import path
from .views import market_research_api

urlpatterns = [
    path('market-research/', market_research_api, name='market_research_api'),
]
