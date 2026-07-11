from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from numbers import Number
from pathlib import Path
from typing import Any
from unicodedata import normalize

import pandas as pd
from django.db import transaction

from apps.portfolios.models import (
    Asset,
    AssetPrice,
    Portfolio,
    PortfolioInitialWeight,
    PortfolioPosition,
)
from apps.portfolios.selectors import asset_prices_get, portfolio_list, portfolio_positions_get


def _asset_code_generate(name: str) -> str:
    normalized = normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    code = "".join(char.lower() if char.isalnum() else "_" for char in normalized)
    return "_".join(part for part in code.split("_") if part)


def _excel_date_to_date(value: Any) -> date | None:
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, Number):
        return date(1899, 12, 30) + timedelta(days=int(value))

    return pd.to_datetime(value).date()


def _decimal_from_excel(value: Any) -> Decimal | None:
    if pd.isna(value):
        return None

    return Decimal(str(value))


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").copy()
    df.columns = [str(column).strip() for column in df.columns]
    return df


@transaction.atomic
def portfolio_data_import_from_excel(*, excel_path: str | Path, initial_value: Decimal) -> dict[str, int]:
    weights_df = _clean_columns(pd.read_excel(excel_path, sheet_name="weights"))
    prices_df = _clean_columns(pd.read_excel(excel_path, sheet_name="Precios"))

    weights_df = weights_df.dropna(subset=["Fecha", "activos"], how="any")
    prices_df = prices_df.dropna(subset=["Dates"], how="any")

    initial_date = _excel_date_to_date(weights_df.iloc[0]["Fecha"])
    if initial_date is None:
        raise ValueError("The weights sheet does not contain an initial date.")

    price_asset_columns = [column for column in prices_df.columns if column != "Dates"]

    assets_by_name: dict[str, Asset] = {}
    for asset_name in price_asset_columns:
        asset, _ = Asset.objects.update_or_create(
            code=_asset_code_generate(asset_name),
            defaults={"name": asset_name},
        )
        assets_by_name[asset_name] = asset

    portfolio_1, _ = Portfolio.objects.update_or_create(
        id=1,
        defaults={
            "name": "Portafolio 1",
            "initial_value": initial_value,
            "initial_date": initial_date,
        },
    )
    portfolio_2, _ = Portfolio.objects.update_or_create(
        id=2,
        defaults={
            "name": "Portafolio 2",
            "initial_value": initial_value,
            "initial_date": initial_date,
        },
    )

    price_count = 0
    for _, row in prices_df.iterrows():
        price_date = _excel_date_to_date(row["Dates"])
        if price_date is None:
            continue

        for asset_name in price_asset_columns:
            price = _decimal_from_excel(row[asset_name])
            if price is None:
                continue

            AssetPrice.objects.update_or_create(
                asset=assets_by_name[asset_name],
                date=price_date,
                defaults={"price": price},
            )
            price_count += 1

    portfolio_columns = {
        "portafolio 1": portfolio_1,
        "portafolio 2": portfolio_2,
    }

    weight_count = 0
    for _, row in weights_df.iterrows():
        asset_name = str(row["activos"]).strip()
        asset = assets_by_name.get(asset_name)
        if asset is None:
            continue

        for column_name, portfolio in portfolio_columns.items():
            weight = _decimal_from_excel(row[column_name])
            if weight is None:
                continue

            PortfolioInitialWeight.objects.update_or_create(
                portfolio=portfolio,
                asset=asset,
                defaults={"weight": weight},
            )
            weight_count += 1

    position_count = portfolio_initial_positions_calculate()

    return {
        "assets": len(assets_by_name),
        "portfolios": 2,
        "prices": price_count,
        "initial_weights": weight_count,
        "positions": position_count,
    }


@transaction.atomic
def portfolio_initial_positions_calculate() -> int:
    position_count = 0

    for portfolio in portfolio_list():
        weights = PortfolioInitialWeight.objects.filter(portfolio=portfolio).select_related("asset")

        for initial_weight in weights:
            price = AssetPrice.objects.get(asset=initial_weight.asset, date=portfolio.initial_date)
            initial_amount = portfolio.initial_value * initial_weight.weight
            quantity = initial_amount / price.price if price.price else Decimal("0")

            PortfolioPosition.objects.update_or_create(
                portfolio=portfolio,
                asset=initial_weight.asset,
                defaults={
                    "quantity": quantity,
                    "initial_amount": initial_amount,
                },
            )
            position_count += 1

    return position_count


def portfolio_timeseries_calculate(
    *,
    portfolio: Portfolio,
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    positions = list(portfolio_positions_get(portfolio=portfolio))
    asset_ids = [position.asset_id for position in positions]
    prices = asset_prices_get(asset_ids=asset_ids, start_date=start_date, end_date=end_date)

    prices_by_date = defaultdict(dict)
    for price in prices:
        prices_by_date[price.date][price.asset_id] = price

    result = []
    for price_date in sorted(prices_by_date):
        date_prices = prices_by_date[price_date]
        if len(date_prices) < len(positions):
            continue

        asset_values = []
        total_value = Decimal("0")

        for position in positions:
            price = date_prices[position.asset_id]
            amount = price.price * position.quantity
            total_value += amount
            asset_values.append(
                {
                    "asset_id": position.asset_id,
                    "asset_name": position.asset.name,
                    "price": price.price,
                    "quantity": position.quantity,
                    "amount": amount,
                }
            )

        for asset_value in asset_values:
            asset_value["weight"] = asset_value["amount"] / total_value if total_value else Decimal("0")

        result.append(
            {
                "date": price_date,
                "value": total_value,
                "assets": asset_values,
            }
        )

    return result
