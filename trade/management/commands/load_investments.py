from django.core.management.base import BaseCommand
from trade.models import Investment
from decimal import Decimal


class Command(BaseCommand):
    help = "Load predefined crypto mining investment plans"

    def handle(self, *args, **kwargs):
        mining_coins = [
            {
                "name": "Bitcoin Pro",
                "abbr": "BTC-PRO",
                "daily_earning": "2.5%",
                "minInvestment": 100,
                "roi": "225%",
                "hashRate": "120 TH/s"
            },
            {
                "name": "Ethereum Max",
                "abbr": "ETH-MAX",
                "daily_earning": "3.2%",
                "minInvestment": 50,
                "roi": "192%",
                "hashRate": "4.5 GH/s"
            },
            {
                "name": "Lite Hash",
                "abbr": "LTC-HASH",
                "daily_earning": "1.8%",
                "minInvestment": 200,
                "roi": "216%",
                "hashRate": "650 GH/s"
            },
            {
                "name": "Ripple Mine",
                "abbr": "XRP-MINE",
                "daily_earning": "2.8%",
                "minInvestment": 75,
                "roi": "210%",
                "hashRate": "1.2 TH/s"
            },
            {
                "name": "Cardano Pool",
                "abbr": "ADA-POOL",
                "daily_earning": "3.5%",
                "minInvestment": 25,
                "roi": "157.5%",
                "hashRate": "8.7 TH/s"
            },
            {
                "name": "Solana Cloud",
                "abbr": "SOL-CLOUD",
                "daily_earning": "4.2%",
                "minInvestment": 10,
                "roi": "126%",
                "hashRate": "12.5 TH/s"
            },
            {
                "name": "Polkadot Grid",
                "abbr": "DOT-GRID",
                "daily_earning": "2.1%",
                "minInvestment": 150,
                "roi": "210%",
                "hashRate": "3.4 TH/s"
            },
            {
                "name": "Binance Power",
                "abbr": "BNB-POWER",
                "daily_earning": "3.8%",
                "minInvestment": 5,
                "roi": "190%",
                "hashRate": "6.8 TH/s"
            }
        ]

        for coin in mining_coins:
            Investment.objects.update_or_create(
                name=coin["name"],
                defaults={
                    "abbr": coin["abbr"],
                    "daily_earning": float(coin["daily_earning"].replace("%", "")),
                    "amount": Decimal(str(coin["minInvestment"])),
                    "roi": float(coin["roi"].replace("%", "")),
                    "hash_rate": float(coin["hashRate"].split()[0]),
                }
            )

        self.stdout.write(self.style.SUCCESS("Investment plans loaded successfully!"))
