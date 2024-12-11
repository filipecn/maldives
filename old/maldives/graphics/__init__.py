import glfw
import OpenGL.GL as gl
import moderngl_window as mglw
from imgui.integrations.glfw import GlfwRenderer
import imgui
from pathlib import Path
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from abc import ABC, abstractmethod
from .scene_object import SceneObject
from .camera import OrthographicCamera


def app(render, width=1280, height=720, window_name="Maldives"):
    """

    :param render:
    :param width:
    :param height:
    :param window_name:
    :return:
    """
    imgui.create_context()
    window = impl_glfw_init(width, height, window_name)
    impl = GlfwRenderer(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        gl.glClearColor(0.3, 0.5, 0.4, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        impl.process_inputs()
        imgui.new_frame()
        render()
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    impl.shutdown()
    glfw.terminate()


def impl_glfw_init(width, height, window_name):
    """

    :param width:
    :param height:
    :param window_name:
    :return:
    """
    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


def draw_table(data, *selected_row):
    imgui.columns(len(data.columns) + 1, "##table")
    imgui.separator()
    imgui.text("")
    imgui.next_column()
    for c in data.columns:
        imgui.text(c)
        imgui.next_column()
    imgui.separator()
    # fill with data
    i = 0
    for _, row in data.iterrows():
        label = str(i)
        clicked, _ = imgui.selectable(label=label,
                                      selected=selected_row == i,
                                      flags=imgui.SELECTABLE_SPAN_ALL_COLUMNS,
                                      )
        if clicked:
            selected_row = i
        hovered = imgui.is_item_hovered()
        imgui.next_column()
        for c in data.columns:
            imgui.text(row[c])
            imgui.next_column()
        i += 1


class App(mglw.WindowConfig, ABC):
    gl_version = (3, 3)
    title = "App"
    resource_dir = (Path(__file__).parent.parent / 'resources').resolve()
    aspect_ratio = None
    scene: [SceneObject]
    camera: OrthographicCamera

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)
        self.scene = []
        self.camera = OrthographicCamera((0, 0), 5, self.wnd)

    def render(self, time: float, frametime: float):
        imgui.new_frame()
        self.render_callback(time)
        imgui.render()
        self.imgui.render(imgui.get_draw_data())
        pass

    @abstractmethod
    def render_callback(self, time: float):
        pass

    def resize(self, width: int, height: int):
        self.imgui.resize(width, height)

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if not imgui.get_io().want_capture_mouse:
            wd = self.camera.unproject_distance(dx, dy)
            control_camera = True
            for o in self.scene:
                o.mouse_drag_event(wd[0], wd[1])
                if o.want_use_mouse:
                    control_camera = False
            if control_camera:
                self.camera.mouse_drag_event(dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if not imgui.get_io().want_capture_mouse:
            control_camera = True
            for o in self.scene:
                o.mouse_scroll_event(x_offset, y_offset)
                if o.want_use_mouse:
                    control_camera = False
            if control_camera:
                self.camera.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)
        if not imgui.get_io().want_capture_mouse:
            sp = x, self.camera.viewport()[1] - y
            wp = self.camera.unproject(sp[0], sp[1])
            for o in self.scene:
                o.mouse_press_event(wp[0], wp[1], button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)
        if not imgui.get_io().want_capture_mouse:
            sp = x, self.camera.viewport()[1] - y
            wp = self.camera.unproject(sp[0], sp[1])
            for o in self.scene:
                o.mouse_release_event(wp[0], wp[1], button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


def run_app(app):
    mglw.run_window_config(app)
