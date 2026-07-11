from django.urls import path

from apps.portfolios.apis import PortfolioValueApi, PortfolioWeightsApi


urlpatterns = [
    path("value/", PortfolioValueApi.as_view(), name="portfolio-value"),
    path("weights/", PortfolioWeightsApi.as_view(), name="portfolio-weights"),
]
