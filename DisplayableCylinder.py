"""
Define Cylinder here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
import numpy as np
import ColorType
import math
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


class DisplayableCylinder(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    stacks = 0
    slices = 0
    radiusX = 0
    radiusY = 0
    radiusZ = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, radius=0.6, height=1, stacks=1, slices=36, color=ColorType.SOFTBLUE):
        super(DisplayableCylinder, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radius, height, stacks, slices, color)

    def generate(self, radius=0.6, height = 1, stacks=1, slices=36, color=ColorType.SOFTBLUE):
        self.radius = radius
        self.height = height
        self.stacks = stacks
        self.slices = slices
        self.color = color

        # Initialize containers for vertices and indices
        vertices = []
        indices = []


        height_values = np.linspace(0, height, stacks+1)

        theta_values = np.linspace(-np.pi, np.pi, slices + 1) 

        # Generate vertices for the cylindrical surface
        for height in height_values:
            
            for theta in theta_values:
                # Vertex position
                x = radius * np.cos(theta)
                y = radius * np.sin(theta)
                z = height

                # Normal vector (points outward radially)
                nx = np.cos(theta)
                ny = np.sin(theta)
                nz = 0
                if height == 0:
                    nx = 0
                    ny = 0
                    nz = -1
                
                if height == self.height:
                    nx = 0
                    ny = 0
                    nz = 1

                # Texture coordinates
                u = 1
                v = 1

                # Add vertex to the list
                vertices.append([x, y, z, nx, ny, nz, *color, u, v])
        vertices.append([0,0,0, 0,0,-1, *color, 1, 1]) #top
        vertices.append([0,0,height, 0,0,1, *color, 1, 1]) #bottom
        # Generate indices for the cylindrical surface
        for stack in range(stacks):
            for slice_ in range(slices):
                # Define the four vertices of the current quad
                top_left = stack * (slices + 1) + slice_
                top_right = top_left + 1
                bottom_left = (stack + 1) * (slices + 1) + slice_
                bottom_right = bottom_left + 1

                # Add first triangle
                indices.extend([top_left, bottom_left, top_right])

                # Add second triangle
                indices.extend([top_right, bottom_left, bottom_right])
        for slice_ in range(slices):
            top_left = slice_
            top_right = top_left + 1
            center = len(vertices)-2
            indices.extend([top_left, top_right, center])
        for slice_ in range(slices+1):
            top_left = slice_+ stacks*(slices+1)
            top_right = top_left + 1
            center = len(vertices)-1
            indices.extend([top_left, top_right, center])
        # Generate vertices and indices for the top and bottom caps
       # self.generate_caps(radius, slices, color, vertices, indices)

        # Convert to numpy arrays for OpenGL
        self.vertices = np.array(vertices, dtype=float)
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

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)
        self.vao.unbind()
