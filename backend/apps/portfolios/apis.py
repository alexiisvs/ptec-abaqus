from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.portfolios.models import Portfolio
from apps.portfolios.selectors import portfolio_list
from apps.portfolios.services import portfolio_timeseries_calculate


def _money_to_string(value: Decimal) -> str:
    return f"{value:.8f}"


def _weight_to_string(value: Decimal) -> str:
    return f"{value:.12f}"


class PortfolioValueApi(APIView):
    class InputSerializer(serializers.Serializer):
        fecha_inicio = serializers.DateField()
        fecha_fin = serializers.DateField()

        def validate(self, attrs):
            if attrs["fecha_inicio"] > attrs["fecha_fin"]:
                raise serializers.ValidationError("fecha_inicio must be lower than or equal to fecha_fin.")
            return attrs

    def get(self, request):
        serializer = self.InputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["fecha_inicio"]
        end_date = serializer.validated_data["fecha_fin"]

        portfolios = []
        for portfolio in portfolio_list():
            series = portfolio_timeseries_calculate(
                portfolio=portfolio,
                start_date=start_date,
                end_date=end_date,
            )
            portfolios.append(
                {
                    "id": portfolio.id,
                    "name": portfolio.name,
                    "series": [
                        {
                            "date": item["date"].isoformat(),
                            "value": _money_to_string(item["value"]),
                        }
                        for item in series
                    ],
                }
            )

        return Response(
            {
                "fecha_inicio": start_date.isoformat(),
                "fecha_fin": end_date.isoformat(),
                "portfolios": portfolios,
            }
        )


class PortfolioWeightsApi(APIView):
    class InputSerializer(serializers.Serializer):
        fecha_inicio = serializers.DateField()
        fecha_fin = serializers.DateField()
        portfolio_id = serializers.IntegerField()

        def validate(self, attrs):
            if attrs["fecha_inicio"] > attrs["fecha_fin"]:
                raise serializers.ValidationError("fecha_inicio must be lower than or equal to fecha_fin.")
            return attrs

    def get(self, request):
        serializer = self.InputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["fecha_inicio"]
        end_date = serializer.validated_data["fecha_fin"]
        portfolio = get_object_or_404(Portfolio, id=serializer.validated_data["portfolio_id"])
        series = portfolio_timeseries_calculate(
            portfolio=portfolio,
            start_date=start_date,
            end_date=end_date,
        )

        assets = []
        if series:
            assets = [
                {
                    "id": asset["asset_id"],
                    "name": asset["asset_name"],
                }
                for asset in series[0]["assets"]
            ]

        return Response(
            {
                "fecha_inicio": start_date.isoformat(),
                "fecha_fin": end_date.isoformat(),
                "portfolio": {
                    "id": portfolio.id,
                    "name": portfolio.name,
                },
                "assets": assets,
                "series": [
                    {
                        "date": item["date"].isoformat(),
                        "value": _money_to_string(item["value"]),
                        "weights": {
                            asset["asset_name"]: _weight_to_string(asset["weight"])
                            for asset in item["assets"]
                        },
                    }
                    for item in series
                ],
            }
        )
