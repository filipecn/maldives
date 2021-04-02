import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import imgui

from pyrr import Matrix44, Vector4


class OrthographicCamera:
    def __init__(self, pos, width, w, h):
        self.__pos = pos
        self.__width = width
        self.__aspect_ratio = w / h
        self.__left = -1
        self.__right = 1
        self.__top = 1
        self.__bottom = -1
        self.__viewport = w, h
        self.update()

    def update(self):
        self.__left = self.__pos[0] - self.__width / 2
        self.__right = self.__pos[0] + self.__width / 2
        self.__top = self.__pos[1] + self.__width / self.__aspect_ratio / 2
        self.__bottom = self.__pos[1] - self.__width / self.__aspect_ratio / 2

    def frustrum(self):
        return self.__left, self.__bottom, self.__right - self.__left, self.__top - self.__bottom

    def pos(self):
        return self.__pos

    def viewport(self):
        return self.__viewport

    def set_pos(self, pos):
        self.__pos = pos
        self.update()

    def set_viewport(self, w, h):
        self.__viewport = w, h
        self.__aspect_ratio = w / h
        self.update()

    def zoom(self, d):
        if d < 0 and self.__width > 1:
            self.__width += 0.1 * self.__width
        else:
            self.__width -= 0.1 * self.__width
        self.update()

    def project(self, x, y):
        return self.__viewport[0] * (x - self.__left) / (self.__right - self.__left), \
               self.__viewport[1] * (y - self.__bottom) / (self.__top - self.__bottom)

    def unproject(self, x, y):
        return x * (self.__right - self.__left) / self.__viewport[0] + self.__left, \
               y * (self.__top - self.__bottom) / self.__viewport[1] + self.__bottom

    def unproject_distance(self, dx, dy):
        return dx * (self.__right - self.__left) / self.__viewport[0], \
               dy * (self.__top - self.__bottom) / self.__viewport[1]

    def transform(self):
        return Matrix44.orthogonal_projection(self.__left, self.__right, self.__bottom, self.__top, -1, 1, dtype='f4')

    def ndc_from_screen_coordinates(self, sp):
        return 2 * sp[0] / self.__viewport[0] - 1, 2 * sp[1] / self.__viewport[1] - 1


def app(render, width=1280, height=720, window_name="Maldives"):
    '''

    :param render:
    :param width:
    :param height:
    :param window_name:
    :return:
    '''
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
