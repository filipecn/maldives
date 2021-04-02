from moderngl_window import geometry
from pyrr import Matrix44
from technical_analysis.candlestick import Candlestick
import graphics
import imgui


class TimeLine:
    def __init__(self):
        self.__date_id = {}
        self.__id_date = []
        self.gap_width = 0.3
        self.day_width = 0.2
        self.model = geometry.quad_2d((1, 1), (0.5, 0.5), False, False)

    def set_from(self, data):
        self.__date_id = {}
        self.__id_date = []
        i = 0
        for date in data:
            self.__date_id[date] = i
            self.__id_date.append(date)
            i += 1

    def add_date(self, date, index):
        self.__date_id[date] = index

    def date_index(self, date):
        if date in self.__date_id:
            return self.__date_id[date]
        return -1

    def pos_index(self, x):
        return int(x / (self.day_width + self.gap_width))

    def index_date(self, i):
        if 0 <= i < len(self.__id_date):
            return self.__id_date[i]
        return None

    def date_pos(self, date):
        i = self.date_index(date)
        return i * (self.gap_width + self.day_width)

    def index_pos(self, i):
        return i * (self.gap_width + self.day_width)

    def intersect(self, x):
        ip = x / (self.day_width + self.gap_width)
        cid = int(ip)
        ip -= cid
        return ip <= self.day_width / (self.day_width + self.gap_width), cid

    def draw(self, prog, data, camera):
        frustrum = camera.frustrum()
        for date in self.__date_id:
            x = self.date_pos(date)
            if frustrum[0] <= x <= frustrum[0] + frustrum[2]:
                prog['color'].value = (0.0, 0.0, 1.0, 0.2)
                prog['m_model'].write(
                    Matrix44.from_translation((x, 0, 0), dtype='f4')
                    *
                    Matrix44.from_scale((self.day_width, 20, 1), dtype='f4')
                )
                self.model.render(prog)


class CandlestickModel:
    def __init__(self, app):
        # box model
        self.model = geometry.quad_2d((1, 1), (0.5, 0.5), False, False)
        # shader
        self.prog = app.load_program('programs/candlestick.glsl')
        self.prog['m_view'].write(Matrix44.identity(dtype='f4'))

    def draw(self, data, camera, timeline):
        self.prog['m_proj'].write(camera.transform())
        frustrum = camera.frustrum()
        for _, row in data.iterrows():
            date = row['Date']
            x = timeline.date_pos(date)
            if frustrum[0] <= x <= frustrum[0] + frustrum[2]:
                open_value = row['Open']
                close_value = row['Close']
                if open_value > close_value:
                    self.prog['color'].value = (1.0, 0.0, 0.0, 1.0)
                else:
                    self.prog['color'].value = (0.0, 1.0, 0.0, 1.0)
                self.prog['m_model'].write(
                    Matrix44.from_translation((x, min([open_value, close_value]), 0), dtype='f4')
                    # Matrix44.from_translation((x, 0, 0), dtype='f4')
                    *
                    Matrix44.from_scale((timeline.day_width, abs(open_value - close_value), 1), dtype='f4')
                )
                self.model.render(self.prog)

    def intersect(self, x, y, data, timeline):
        # compute candle index
        i = timeline.intersect(x)
        if 0 <= i[1] < len(data) and i[0]:
            row = data.iloc[i[1]]
            open_value = row['Open']
            close_value = row['Close']
            if min([open_value, close_value]) <= y <= max([open_value, close_value]):
                return Candlestick(row, i[1])
        return None

    def draw_gui(self, camera, data, timeline):
        x = imgui.get_mouse_pos().x
        y = camera.viewport()[1] - imgui.get_mouse_pos().y
        p = camera.unproject(x, y)
        r = self.intersect(p[0], p[1], data, timeline)
        if r is not None:
            wp = x + 20, camera.viewport()[1] - y - 100
            imgui.set_next_window_position(wp[0], wp[1])
            imgui.set_next_window_bg_alpha(0.8)
            imgui.begin("pointer", False,
                        imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
            imgui.text("Date: " + str(r.date))
            imgui.separator()
            imgui.text("Low: %.2f" % float(r.min_value))
            imgui.text("Max: %.2f" % float(r.max_value))
            imgui.text("Open: %.2f" % float(r.open_value))
            imgui.text("Close: %.2f" % float(r.close_value))
            imgui.end()


class CandlestickPatternModel:
    def __init__(self):
        self.model = geometry.quad_2d((1, 1), (0.5, 0.5), False, False)

    def draw(self, prog, data, camera, timeline):
        frustrum = camera.frustrum()
        for _, row in data.iterrows():
            date = row['Date']
            x = timeline.date_pos(date)
            if frustrum[0] <= x <= frustrum[0] + frustrum[2]:
                prog['color'].value = (1.0, 1.0, 0.0, 1.0)
                prog['m_model'].write(
                    Matrix44.from_translation((x, camera.frustrum()[1], 0), dtype='f4')
                    *
                    Matrix44.from_scale((timeline.day_width, 1, 1), dtype='f4')
                )
                self.model.render(prog)

    def draw_gui(self, camera, data, timeline):
        io = imgui.get_io()
        if not io.want_capture_mouse:
            x = imgui.get_mouse_pos().x
            y = camera.viewport()[1] - imgui.get_mouse_pos().y
            p = camera.unproject(x, y)
            i = timeline.intersect(p[0])
            if i[0]:
                date = timeline.index_date(i[1])
                if date is not None:
                    df = data[data.Date == date]
                    wp = x + 20, camera.viewport()[1] - y - 100
                    imgui.set_next_window_position(wp[0], wp[1])
                    imgui.set_next_window_bg_alpha(0.8)
                    imgui.begin("pointer", False,
                                imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
                    imgui.text("Date: " + str(date))
                    for index, row in df.iterrows():
                        imgui.separator()
                        imgui.text(row["Pattern"] + ": " + str(row["CandleTime"]))
                    imgui.end()

        pass


class MeasureModel:
    def __init__(self, app):
        # box model
        self.model = geometry.quad_2d((1, 1), (0.5, 0.5), False, False)
        # shaders
        self.prog = app.load_program('programs/screen_element.glsl')
        # control
        self.dragging = False
        # NDC
        self.drag_start = 0, 0
        self.drag_end = 0, 0
        # W
        self.start = 0, 0
        self.end = 0, 0

    def draw(self):
        if self.dragging:
            self.prog['color'].value = (0.0, 1.0, 0.0, 0.3)
            if self.start[1] > self.end[1]:
                self.prog['color'].value = (1.0, 0.0, 0.0, 0.3)
            self.prog['transform'].write(
                Matrix44.from_translation((self.drag_start[0], self.drag_start[1], 0), dtype='f4')
                *
                Matrix44.from_scale((self.drag_end[0] - self.drag_start[0], self.drag_end[1] - self.drag_start[1], 1),
                                    dtype='f4')
            )
            self.model.render(self.prog)

    def draw_gui(self, sp, wp, camera):
        # render price pointer
        win_p = sp[0] - 100, camera.viewport()[1] - sp[1] - 30
        imgui.set_next_window_position(win_p[0], win_p[1])
        imgui.set_next_window_bg_alpha(0.1)
        imgui.begin("mouse_pointer", False,
                    imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        imgui.text("R$ %.2f" % wp[1])
        imgui.end()
        # render box measure
        if self.dragging:
            ss = camera.project(self.start[0], self.start[1])
            se = camera.project(self.end[0], self.end[1])
            win_p = (ss[0] + se[0]) / 2, camera.viewport()[1] - (ss[1] + se[1]) / 2
            imgui.set_next_window_position(win_p[0], win_p[1])
            imgui.set_next_window_bg_alpha(0.9)
            imgui.begin("box_measure", False,
                        imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
            imgui.text("R$ %.2f -> %.2f" % (self.start[1], self.end[1]))
            imgui.text("Profit: R$ %.2f (%.2f%%)" % (
                self.end[1] - self.start[1], ((self.end[1] - self.start[1]) / self.start[1] * 100)))
            imgui.end()


class CandleStickChart:
    def __init__(self, app):
        # data
        self.price_data = None
        self.pattern_data = None
        # chart elements
        self.timeline = TimeLine()
        self.candlestick_model = CandlestickModel(app)
        self.candlestick_patterns_model = CandlestickPatternModel()
        # graphics
        self.viewport = app.wnd
        self.camera = None
        # measures
        self.measures = MeasureModel(app)

    def set_data(self, price_data, pattern_data):
        self.price_data = price_data
        self.pattern_data = pattern_data
        # update timeline
        self.timeline.set_from(price_data['Date'])

        # focus camera
        last_x = self.timeline.index_pos(len(price_data))
        last_y = price_data.iloc[-1]["Open"]
        width = self.timeline.index_pos(14)  # 7 days radius
        self.camera = graphics.OrthographicCamera((last_x, last_y), width, self.viewport.width,
                                                  self.viewport.height)

    def render(self):
        self.candlestick_model.draw(self.price_data, self.camera, self.timeline)

        sp = imgui.get_mouse_pos().x, self.camera.viewport()[1] - imgui.get_mouse_pos().y
        self.measures.drag_end = self.camera.ndc_from_screen_coordinates(sp)
        self.measures.end = self.camera.unproject(sp[0], sp[1])
        self.measures.draw()

    def render_gui(self):
        # compute mouse screen position
        sp = imgui.get_mouse_pos().x, self.camera.viewport()[1] - imgui.get_mouse_pos().y
        # compute mouse world position
        wp = self.camera.unproject(sp[0], sp[1])
        self.measures.draw_gui(sp, wp, self.camera)
        if not self.measures.dragging:
            self.candlestick_model.draw_gui(self.camera, self.price_data, self.timeline)
            self.candlestick_patterns_model.draw_gui(self.camera, self.pattern_data, self.timeline)

    def mouse_drag_event(self, dx, dy):
        io = imgui.get_io()
        if not self.measures.dragging:
            d = self.camera.unproject_distance(dx, dy)
            self.camera.set_pos((self.camera.pos()[0] - d[0], self.camera.pos()[1] + d[1]))

    def mouse_scroll_event(self, x_offset, y_offset):
        self.camera.zoom(y_offset)

    def mouse_press_event(self, x, y, button):
        if button == 2:
            self.measures.dragging = True
            sp = x, self.camera.viewport()[1] - y
            self.measures.drag_start = self.camera.ndc_from_screen_coordinates(sp)
            self.measures.start = self.camera.unproject(sp[0], sp[1])

    def mouse_release_event(self, x: int, y: int, button: int):
        self.measures.dragging = False
