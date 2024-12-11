import imgui
from maldives.bot.models.wallet import Wallet
from maldives.bot.strategies.strategy import Strategy


class StrategyBacktraceWindow:
    wallet: Wallet
    strategy: Strategy

    def __init__(self):
        pass

    def draw(self):
        imgui.begin("Strategy Backtrace Test")
        imgui.end()
