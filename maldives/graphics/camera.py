from pyrr import Matrix44


class OrthographicCamera:
    def __init__(self, pos, width, viewport):
        self.__pos = pos
        self.__width = width
        self.__aspect_ratio = viewport.width / viewport.height
        self.__left = -1
        self.__right = 1
        self.__top = 1
        self.__bottom = -1
        self.__viewport = viewport.width, viewport.height
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

    def mouse_drag_event(self, dx, dy):
        d = self.unproject_distance(dx, dy)
        self.set_pos((self.pos()[0] - d[0], self.pos()[1] + d[1]))

    def mouse_scroll_event(self, x_offset, y_offset):
        self.zoom(y_offset)
