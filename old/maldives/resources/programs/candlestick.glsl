#version 330

#if defined VERTEX_SHADER

in vec3 in_position;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

void main() {
    vec4 p = m_view * m_model * vec4(in_position, 1.0);
    gl_Position =  m_proj * p;
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;
uniform vec4 color;

void main() {
    fragColor = color;
}
#endif