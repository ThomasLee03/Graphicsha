"""
Define ellipsoid here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

import ctypes
from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
import numpy as np
import ColorType
import math
from PIL import Image
try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")


class DisplayableEllipsoid(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    texture_id = None

    # stores current torus's information, read-only
    stacks = 0
    slices = 0
    radiusX = 0
    radiusY = 0
    radiusZ = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=ColorType.DARKGREEN):
        super(DisplayableEllipsoid, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radiusX, radiusY, radiusZ, stacks, slices, color)

    def load_texture(self, file_path):
        img = Image.open(file_path)
        img_data = np.array(img.convert("RGBA"), dtype=np.uint8)
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, img.width, img.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        # Set texture parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        return texture_id

    def generate(self, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=ColorType.SOFTBLUE):
        self.radiusX = radiusX
        self.radiusY = radiusY
        self.radiusZ = radiusZ
        self.stacks = stacks
        self.slices = slices
        self.color = color

        vertices = []
        indices = []
        
        # Generate phi and theta values
        phi_values = np.linspace(-np.pi / 2, np.pi / 2, stacks + 1) 
        theta_values = np.linspace(-np.pi, np.pi, slices + 1) 

        for phi in phi_values:
            for theta in theta_values:
                # Calculate vertex position
                x = radiusX * np.cos(phi) * np.cos(theta)
                y = radiusY * np.cos(phi) * np.sin(theta)
                z = radiusZ * np.sin(phi)
                norm = np.sqrt((x**2) + (y**2) + (z**2))

                nx = x / norm
                ny = y / norm
                nz = z / norm

                u = 0.5 + (math.atan2(z, x) / (2 * math.pi))  # Map longitude to [0, 1]
                v = 0.5 - (math.asin(y / radiusY) / math.pi)  # Map latitude to [0, 1]
                


                vertices.append([x, y, z, nx, ny, nz, *color, u, v])
        
        self.vertices = np.array(vertices, dtype=float)

        for i in range(stacks):
            for j in range(slices):
                top_left = i * (slices + 1) + j
                top_right = top_left + 1
                bottom_left = (i + 1) * (slices + 1) + j
                bottom_right = bottom_left + 1
                # Add first triangle
                indices.extend([top_left, bottom_left, top_right])

                # Add second triangle
                indices.extend([top_right, bottom_left, bottom_right])
        
        self.indices = np.array(indices, dtype=np.uint32)
    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems which don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)
        self.texture_id = self.load_texture("./assets/earth.jpg")
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glEnableVertexAttribArray(3)  # Enable the texture attribute (index 3 in the shader)
        gl.glVertexAttribPointer(
            3, 2, gl.GL_FLOAT, gl.GL_FALSE,
            self.vertices.shape[1] * ctypes.sizeof(ctypes.c_float),  # Stride: size of one vertex
            ctypes.c_void_p(9 * ctypes.sizeof(ctypes.c_float))  # Offset: texture coordinates start at column 9
        )

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)
        self.vao.unbind()
