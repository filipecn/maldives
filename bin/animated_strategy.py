from maldives.graphics import *
from maldives.technical_analysis import TA
from maldives.bot.strategies.strategy import Strategy
from maldives.graphics.candlestick_model import CandleStickChart
from yahooquery import Ticker
import pandas as pd
import numpy as np

from maldives.graphics.curve import CurveModel


def get_closest_resistance(values_and_indices, price, current_index):
    values = values_and_indices[0]
    indices = values_and_indices[1]
    value = 10000000
    resistance_index = -1
    for i in range(len(values)):
        avg = np.array(values[i]).mean()
        if price <= avg <= value and min(indices[i]) <= current_index:
            value = avg
            resistance_index = i
    return value, resistance_index


def get_closest_support(values_and_indices, price, current_index):
    values = values_and_indices[0]
    indices = values_and_indices[1]
    value = -10000000
    support_index = -1
    for i in range(len(values)):
        avg = np.array(values[i]).mean()
        if value <= avg <= price and min(indices[i]) <= current_index:
            value = avg
            support_index = i
    return value, support_index


class ResistanceLine:
    def __init__(self, wcg, values, ids, timeline, color):
        self.model = CurveModel(wcg)
        self.model.color = color
        self.model.set_horizontal_line(np.array(values).mean(), 1000, timeline.index_pos(min(ids)))

    def draw(self, camera):
        self.model.draw(camera)


class CustomStrategy(App, Strategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # historical data
        # self.data = Ticker('petr4.sa').history(period="ytd").reset_index(drop=False)
        self.data = pd.read_csv('../data/petr4.sa')

        # strategy specifics
        self.ta = TA(self.data)
        self.support_lines_data = self.ta.resistance_lines('s')
        self.resistance_lines_data = self.ta.resistance_lines('r')
        print(self.ta.candle_directions())
        print(self.ta.reversals())
        # simulation
        self.tick_count = len(self.data)
        self.current_tick = 0
        # scene
        self.scene.append(CandleStickChart(self))
        self.scene[0].set_data(self.data)
        # focus camera
        last_x = self.scene[0].timeline.index_pos(len(self.data))
        last_y = self.data.iloc[-1]["open"]
        width = self.scene[0].timeline.index_pos(14)  # 7 days radius
        self.camera = OrthographicCamera((last_x, last_y), width, self.wnd)
        # resistance lines
        self.resistance_lines = []
        for i in range(len(self.resistance_lines_data[0])):
            self.resistance_lines.append(
                ResistanceLine(self, self.resistance_lines_data[0][i], self.resistance_lines_data[1][i],
                               self.scene[0].timeline, (1, 0, 0, 1.0)))
        # support lines
        self.support_lines = []
        for i in range(len(self.support_lines_data[0])):
            self.support_lines.append(
                ResistanceLine(self, self.support_lines_data[0][i], self.support_lines_data[1][i],
                               self.scene[0].timeline, (0, 1, 0, 1.0)))

    # render
    def render_callback(self, time: float):
        for o in self.scene:
            o.draw(self.camera)
        for o in self.scene:
            o.draw_gui(self.camera)
        # self.scene[0].render(self.camera)
        # self.scene[0].render_gui(self.camera)
        # for rl in self.resistance_lines:
        #     rl.draw(self.scene[0].camera)
        # for sl in self.support_lines:
        #     sl.draw(self.scene[0].camera)
        # self.support.draw(self.scene[0].camera)
        # self.resistance.draw(self.scene[0].camera)
        # move in the timeline
        mouse_price = self.scene[0].measures.current_pointer[1]
        mouse_tick = self.scene[0].timeline.pos_index(self.scene[0].measures.current_pointer[0])

        old_tick = self.current_tick
        self.current_tick = int(time) % self.tick_count
        if old_tick != self.current_tick:
            self.run()

        # mouse_price = self.data.iloc[self.current_tick]['close']
        # mouse_tick = self.current_tick
        # self.scene[0].candlestick_model.upper_cut = self.current_tick

        current_support = get_closest_support(self.support_lines_data, mouse_price, mouse_tick - 1)
        if current_support[0] <= mouse_price and current_support[1] >= 0:
            self.support_lines[current_support[1]].draw(self.camera)
        current_resistance = get_closest_resistance(self.resistance_lines_data, mouse_price, mouse_tick - 1)
        if current_resistance[0] >= mouse_price and current_resistance[1] >= 0:
            self.resistance_lines[current_resistance[1]].draw(self.camera)

    # run strategy
    def run(self):

        pass
        # support_line = last_resistance_line(self.support_lines, self.current_tick)
        # self.support.set_horizontal_line(
        #     support_line,
        #     self.data.iloc[self.current_tick]['close'],
        # self.scene[0].timeline.index_pos(self.current_tick)
        # )
        # resistance_line = last_resistance_line(self.resistance_lines, self.current_tick)
        # self.resistance.set_horizontal_line(
        #     resistance_line,
        #     self.data.iloc[self.current_tick]['close'],
        # self.scene[0].timeline.index_pos(self.current_tick)
        # )


if __name__ == "__main__":
    run_app(CustomStrategy)
