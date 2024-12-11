import imgui
from maldives.bot.models.wallet import Wallet


class MyWalletWindow:
    wallet: Wallet

    def __init__(self, wallet: Wallet):
        self.wallet = wallet

    def draw(self):
        imgui.begin('My Wallet')
        imgui.text('total balance: %.2f' % self.wallet.balance())
        for symbol, info in self.wallet.assets.items():
            imgui.text('%.2f%%' % self.wallet.allocation_pct(symbol))
            imgui.same_line()
            imgui.text(symbol)
            imgui.same_line()
            imgui.text(str(info['mean_price']))
            imgui.same_line()
            imgui.text(str(info['amount']))
            imgui.same_line()
            imgui.text(str(info['balance']))
        imgui.end()
