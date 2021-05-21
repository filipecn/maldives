import pandas as pd
import os
import imgui
from datetime import datetime
import maldives.data.fundamentus as fund
from maldives.technical_analysis import TA, get_closest_support, get_closest_resistance
from maldives.graphics.curve import *
from maldives.bot.brokers.yq_broker import YQBroker
from maldives.bot.exchanges.binance_exchange import BinanceExchange
from maldives.bot.models.wallet import Wallet
from my_wallet_window import MyWalletWindow
import logging

from maldives.graphics.candlestick_model import *


class TAData:
    curves: [CurveModel]
    resistance_lines_data: [[]]
    resistance_lines: [CurveModel]
    resistance_line_count: int
    ta: TA

    def __init__(self, wcg):
        self.wcg = wcg
        self.resistance_lines_data = []
        self.resistance_lines = []

    def set_data(self, data, timeline: TimeLine):
        self.ta = TA(data)
        support_lines_data = self.ta.resistance_lines('s')
        self.resistance_lines_data = self.ta.resistance_lines('r')

        self.resistance_line_count = len(self.resistance_lines_data[0])

        self.resistance_lines_data[0].extend(support_lines_data[0])
        self.resistance_lines_data[1].extend(support_lines_data[1])

        def horizontal_line(values, ids, color):
            model = CurveModel(self.wcg)
            model.color = color
            model.set_horizontal_line(np.array(values).mean(), 1000, timeline.index_pos(min(ids)))
            return model

        for i in range(len(self.resistance_lines_data[0])):
            self.resistance_lines.append(
                horizontal_line(self.resistance_lines_data[0][i], self.resistance_lines_data[1][i],
                                (1, 0, 0, 1)))

    def draw_closest_resistance_line(self, c: OrthographicCamera, price: float, current_index: int):
        if not len(self.resistance_lines_data):
            return
        r = get_closest_resistance(self.resistance_lines_data, price, current_index)
        if r[0] >= price and r[1] >= 0:
            self.resistance_lines[r[1]].draw(c)

    def draw_closest_support_line(self, c: OrthographicCamera, price: float, current_index: int):
        if not len(self.resistance_lines_data):
            return
        r = get_closest_support(self.resistance_lines_data, price, current_index)
        if r[0] <= price and r[1] >= 0:
            self.resistance_lines[r[1]].draw(c)


class MainApp(App):
    # dealers
    cripto_dealer: BinanceExchange
    b3_dealer: YQBroker
    # wallets
    cripto_wallet: Wallet
    b3_wallet: Wallet
    # windows
    my_wallet_window: MyWalletWindow
    # gui
    symbol_list = fund.get_symbol_list("../tests/raw_fund_html", False)
    input_text = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # scene
        self.ta_data = TAData(self)
        self.scene.append(CandleStickChart(self))
        self.ta = None
        self.curves = []
        self.b3_dealer = YQBroker()
        self.b3_wallet = Wallet()
        self.my_wallet_window = MyWalletWindow(self.b3_wallet)

    # render
    def render_callback(self, time: float):
        self.my_wallet_window.draw()
        self.menu_bar()
        for o in self.scene:
            o.draw(self.camera)
        for o in self.scene:
            o.draw_gui(self.camera)
        for c in self.curves:
            c.draw(self.camera)

        mouse_price = self.scene[0].measures.current_pointer[1]
        mouse_tick = self.scene[0].timeline.pos_index(self.scene[0].measures.current_pointer[0])
        self.ta_data.draw_closest_support_line(self.camera, mouse_price, mouse_tick)
        self.ta_data.draw_closest_resistance_line(self.camera, mouse_price, mouse_tick)

    def cleanup(self):
        del self.my_wallet_window
        del self.b3_wallet

    def menu_bar(self):
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )
                if clicked_quit:
                    self.cleanup()
                    exit(0)
                imgui.end_menu()
            changed, value = imgui.input_text("", self.input_text, 30)
            if changed:
                imgui.set_next_window_position(imgui.get_item_rect_min().x,
                                               imgui.get_item_rect_max().y)
                imgui.set_next_window_size(imgui.get_item_rect_size().x, 0)
                if imgui.begin("##popup", False,
                               imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE):
                    for index, row in self.symbol_list.iterrows():
                        if value.upper() in row[0]:
                            _, _ = imgui.selectable(row[0] + " - " + row[2])
                            if imgui.is_item_clicked():
                                self.input_text = row[0]
                                self.load_symbol(str(row[0]).lower())
                imgui.end()
            imgui.end_main_menu_bar()

    def load_symbol(self, symbol):
        logging.info("loading symbol %s", symbol)
        self.b3_dealer.historical_symbol_ticker_candle(symbol,
                                                       datetime(year=2021, day=1, month=1))
        # data = pd.read_csv('../data/petr4.sa')
        data = self.b3_dealer.historical_data[
            self.b3_dealer.historical_data.symbol == self.b3_dealer.get_symbol(symbol)]
        if len(data):
            self.scene[0].set_data(data)
            self.ta_data.set_data(data, self.scene[0].timeline)
            # ta
            self.ta = TA(data)
            self.curves.append(CurveModel(self))
            self.curves[0].set_from_data(self.ta.ema(3), self.scene[0].timeline)
            self.curves.append(CurveModel(self))
            self.curves[1].set_from_data(self.ta.ema(10), self.scene[0].timeline)
            self.curves[1].color = (0.0, 0.0, 1.0, 1.0)
            # focus camera
            last_x = self.scene[0].timeline.index_pos(len(data))
            last_y = data.iloc[-1]["open"]
            width = self.scene[0].timeline.index_pos(14)  # 7 days radius
            self.camera = OrthographicCamera((last_x, last_y), width, self.wnd)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s",
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    run_app(MainApp)
