
from OpenGL.GL import *
from OpenGL.GLUT import *

class Shader:
    def __init__(self):
        self.shader_list = []

    @staticmethod
    def create_shader(shaderType, shaderCode):
        shader_ID = glCreateShader(shaderType)
        glShaderSource(shader_ID, shaderCode)
        glCompileShader(shader_ID)

        status = None
        glGetShaderiv(shader_ID, GL_COMPILE_STATUS, status)
        if status == GL_FALSE:
            strInfoLog = glGetShaderInfoLog(shader_ID)
            strShaderType = ""
            if shaderType is GL_VERTEX_SHADER:
                strShaderType = "vertex"
            elif shaderType is GL_GEOMETRY_SHADER:
                strShaderType = "geometry"
            elif shaderType is GL_FRAGMENT_SHADER:
                strShaderType = "fragment"

            print("Compilation failure for " + strShaderType + " shader:\n" + strInfoLog)

        return shader_ID