from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from apps.portfolios.services import portfolio_data_import_from_excel


class Command(BaseCommand):
    help = "Load portfolio data from data/datos.xlsx."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "excel_path",
            nargs="?",
            default=str(settings.BASE_DIR.parent / "data" / "datos.xlsx"),
        )

    def handle(self, *args, **options) -> None:
        excel_path = Path(options["excel_path"])
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        summary = portfolio_data_import_from_excel(
            excel_path=excel_path,
            initial_value=Decimal(settings.INITIAL_PORTFOLIO_VALUE),
        )

        self.stdout.write(self.style.SUCCESS("Portfolio data loaded."))
        for key, value in summary.items():
            self.stdout.write(f"{key}: {value}")
