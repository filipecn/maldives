import pandas as pd
import os
import imgui
import data.investing_com as inv
import data.fundamentus as fund
import data.yfinance_api as yfc
import graphics
from pathlib import Path
from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window import geometry
from moderngl_window.integrations.imgui import ModernglWindowRenderer

from graphics.candlestick_model import *

selected_symbol = "PETR4"
input_text = ""
csl = inv.load_data("../investing_com_data/")
print(len(csl))
csl = csl[csl.Candle == "Current"]
print(len(csl))
symbol_list = fund.get_symbol_list("../tests/raw_fund_html", False)
print(csl[csl.Symbol == selected_symbol])


# compressed = inv.compress_cs_patterns(csl)

# for symbol, patterns in compressed.items():
#     for pattern, candle_times in patterns.items():
#         for candle_time, time_frames in candle_times.items():
#             for time_frame, registers in time_frames.items():
#                 for register in registers:
#                     print(symbol, pattern, candle_time, time_frame, register.date, register.candle)
#     break
# exit(1)


def symbol_data_file():
    return "../data/" + selected_symbol + '_yf_data'


def check_data():
    if not os.path.exists(symbol_data_file()):
        yfc.download(selected_symbol, symbol_data_file())


class WindowEvents(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "imgui Integration"
    resource_dir = (Path(__file__).parent / 'resources').resolve()
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.petr4_h = pd.read_csv("../data/" + selected_symbol + '_yf_data')

        self.candlestick_chart = CandleStickChart(self)
        self.candlestick_chart.set_data(self.petr4_h, csl[csl.Symbol == selected_symbol])

    def render(self, time: float, frametime: float):
        global selected_symbol
        global input_text
        self.candlestick_chart.render()
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )
                if clicked_quit:
                    exit(1)
                imgui.end_menu()
            changed, value = imgui.input_text("", input_text, 30)
            if changed:
                imgui.set_next_window_position(imgui.get_item_rect_min().x,
                                               imgui.get_item_rect_max().y)
                imgui.set_next_window_size(imgui.get_item_rect_size().x, 0)
                if imgui.begin("##popup", False,
                               imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE):
                    for index, row in symbol_list.iterrows():
                        if value.upper() in row[0]:
                            opened, selected = imgui.selectable(row[0] + " - " + row[2])
                            if imgui.is_item_clicked():
                                input_text = row[0]
                                selected_symbol = row[0]
                imgui.end()
            if imgui.button("download"):
                yfc.download(selected_symbol, symbol_data_file())
            imgui.end_main_menu_bar()

        if not imgui.get_io().want_capture_mouse:
            self.candlestick_chart.render_gui()
        # if len(df):
        #     graphics.draw_table(df, 0)

        imgui.show_test_window()

        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if not imgui.get_io().want_capture_mouse:
            self.candlestick_chart.mouse_drag_event(dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if not imgui.get_io().want_capture_mouse:
            self.candlestick_chart.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)
        if not imgui.get_io().want_capture_mouse:
            self.candlestick_chart.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)
        if not imgui.get_io().want_capture_mouse:
            self.candlestick_chart.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


if __name__ == "__main__":
    mglw.run_window_config(WindowEvents)
