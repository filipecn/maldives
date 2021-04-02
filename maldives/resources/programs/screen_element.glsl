#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
uniform mat4 transform;

void main() {
    gl_Position =  transform * vec4(in_position, 1.0);
}

    #elif defined FRAGMENT_SHADER

out vec4 fragColor;
uniform vec4 color;

void main() {
    fragColor = color;
}
    #endif
