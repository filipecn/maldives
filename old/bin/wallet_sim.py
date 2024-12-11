from datetime import datetime
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from maldives.bot.brokers.yq_broker import YQBroker
from maldives.bot.models.wallet import Wallet

logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=logging.INFO,
                    datefmt="%H:%M:%S")

dealer = YQBroker()
wallet = Wallet()
wallet.append('petr4', 50)
wallet.append('vale3', 50)
results = wallet.backtrace(dealer, datetime(year=2021, day=1, month=1))
print(results)
