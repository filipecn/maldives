import moderngl
import moderngl_window as mglw
import numpy as np
from pyrr import Matrix44

from maldives.graphics import OrthographicCamera


class CurveModel:
    vertices: np.array
    wcg: mglw.WindowConfig
    color = (1.0, 1.0, 1.0, 1.0)

    def __init__(self, wcg: mglw.WindowConfig):
        self.wcg = wcg
        self.program = wcg.load_program('programs/candlestick.glsl')
        self.program['m_view'].write(Matrix44.identity(dtype='f4'))
        self.program['m_model'].write(Matrix44.identity(dtype='f4'))

        self.vertices = np.array([0, 20, 0, 1000, 20, 0])
        self.vbo = wcg.ctx.buffer(self.vertices.astype('f4').tobytes())
        self.vao = wcg.ctx.vertex_array(self.program,
                                        [(self.vbo, '3f', 'in_position')])

    def __del__(self):
        self.vao.release()
        self.vbo.release()

    def set_horizontal_line(self, y, xmax=1000, xmin=0):
        self.set_vertices([xmin, y, 0, xmax, y, 0])

    def set_vertices(self, vertices):
        self.vao.release()
        self.vbo.release()
        self.vertices = np.array(vertices)
        self.vbo = self.wcg.ctx.buffer(self.vertices.astype('f4').tobytes())
        self.vao = self.wcg.ctx.vertex_array(self.program,
                                             [(self.vbo, '3f', 'in_position')])

    def set_from_data(self, data, timeline):
        buffer = []
        data_list = data.values.tolist()
        for i in range(len(data_list)):
            buffer.append(timeline.index_pos(i) + timeline.day_width / 2.0)
            buffer.append(data_list[i])
            buffer.append(0)
        self.set_vertices(buffer)

    def draw(self, camera: OrthographicCamera):
        self.program['m_proj'].write(camera.transform())
        self.program['color'].value = self.color
        self.vao.render(mode=moderngl.LINE_STRIP)
