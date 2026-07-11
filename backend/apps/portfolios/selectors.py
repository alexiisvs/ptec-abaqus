from datetime import date
from typing import Iterable

from django.db.models import QuerySet

from apps.portfolios.models import AssetPrice, Portfolio, PortfolioPosition


def portfolio_list() -> QuerySet[Portfolio]:
    return Portfolio.objects.all().order_by("id")


def portfolio_positions_get(*, portfolio: Portfolio) -> QuerySet[PortfolioPosition]:
    return (
        PortfolioPosition.objects.filter(portfolio=portfolio)
        .select_related("asset", "portfolio")
        .order_by("asset__name")
    )


def asset_prices_get(
    *,
    asset_ids: Iterable[int],
    start_date: date,
    end_date: date,
) -> QuerySet[AssetPrice]:
    return (
        AssetPrice.objects.filter(
            asset_id__in=list(asset_ids),
            date__gte=start_date,
            date__lte=end_date,
        )
        .select_related("asset")
        .order_by("date", "asset__name")
    )
