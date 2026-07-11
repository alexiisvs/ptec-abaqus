from django.db import models


class Asset(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Portfolio(models.Model):
    name = models.CharField(max_length=128)
    initial_value = models.DecimalField(max_digits=24, decimal_places=8)
    initial_date = models.DateField()

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name


class AssetPrice(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date = models.DateField()
    price = models.DecimalField(max_digits=24, decimal_places=8)

    class Meta:
        ordering = ["date", "asset__name"]
        constraints = [
            models.UniqueConstraint(fields=["asset", "date"], name="unique_asset_price_date"),
        ]
        indexes = [
            models.Index(fields=["date"], name="asset_price_date_idx"),
            models.Index(fields=["asset", "date"], name="asset_price_asset_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.asset.name} - {self.date}"


class PortfolioInitialWeight(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="initial_weights")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="initial_weights")
    weight = models.DecimalField(max_digits=20, decimal_places=12)

    class Meta:
        ordering = ["portfolio_id", "asset__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "asset"],
                name="unique_portfolio_initial_weight_asset",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.portfolio.name} - {self.asset.name}"


class PortfolioPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="positions")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="positions")
    quantity = models.DecimalField(max_digits=30, decimal_places=12)
    initial_amount = models.DecimalField(max_digits=24, decimal_places=8)

    class Meta:
        ordering = ["portfolio_id", "asset__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "asset"],
                name="unique_portfolio_position_asset",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.portfolio.name} - {self.asset.name}"
