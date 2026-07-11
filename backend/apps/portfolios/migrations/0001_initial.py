import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Portfolio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("initial_value", models.DecimalField(decimal_places=8, max_digits=24)),
                ("initial_date", models.DateField()),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="AssetPrice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("price", models.DecimalField(decimal_places=8, max_digits=24)),
                (
                    "asset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prices", to="portfolios.asset"),
                ),
            ],
            options={
                "ordering": ["date", "asset__name"],
                "indexes": [
                    models.Index(fields=["date"], name="asset_price_date_idx"),
                    models.Index(fields=["asset", "date"], name="asset_price_asset_date_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("asset", "date"), name="unique_asset_price_date"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PortfolioInitialWeight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weight", models.DecimalField(decimal_places=12, max_digits=20)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="initial_weights",
                        to="portfolios.asset",
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="initial_weights",
                        to="portfolios.portfolio",
                    ),
                ),
            ],
            options={
                "ordering": ["portfolio_id", "asset__name"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("portfolio", "asset"),
                        name="unique_portfolio_initial_weight_asset",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="PortfolioPosition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.DecimalField(decimal_places=12, max_digits=30)),
                ("initial_amount", models.DecimalField(decimal_places=8, max_digits=24)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="portfolios.asset",
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="portfolios.portfolio",
                    ),
                ),
            ],
            options={
                "ordering": ["portfolio_id", "asset__name"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("portfolio", "asset"),
                        name="unique_portfolio_position_asset",
                    ),
                ],
            },
        ),
    ]
