"""
Define Torus here.
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

##### TODO 6/BONUS 6: Texture Mapping
# Requirements:
#   1. Set up each object's vertex texture coordinates(2D) to the self.vertices 9:11 columns
#   (i.e. the last two columns). Tell OpenGL how to interpret these two columns:
#   you need to set up attribPointer in the Displayable object's initialize method.
#   2. Generate texture coordinates for the torus and sphere. Use “./assets/marble.jpg” for the torus and
#   “./assets/earth.jpg” for the sphere as the texture image.
#   There should be no seams in the resulting texture-mapped model.

class DisplayableTorus(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    nsides = 0
    rings = 0
    innerRadius = 0
    outerRadius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        super(DisplayableTorus, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(innerRadius, outerRadius, nsides, rings, color)

    def generate(self, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.nsides = nsides
        self.rings = rings
        self.color = color

        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        vertices = []
        indices = []

        phi_values = np.linspace(-np.pi, np.pi, nsides + 1) 
        theta_values = np.linspace(-np.pi, np.pi, rings + 1) 

        for phi in phi_values:
            for theta in theta_values:
                x = (outerRadius + innerRadius*np.cos(phi))*np.cos(theta)
                y = (outerRadius + innerRadius*np.cos(phi))*np.sin(theta)
                z = innerRadius*np.sin(phi)

                nx, ny, nz = self.torus_norm(x, y, z, outerRadius)
                u=1
                v=1
                vertices.append([x, y, z, nx, ny, nz, *color, u, v])
                
        self.vertices = np.array(vertices, dtype=float)
        # Generate indices
        
        for i in range(nsides):
            for j in range(rings):
                # Calculate the four vertices of the current quad
                top_left = i * (rings + 1) + j
                top_right = top_left + 1
                bottom_left = (i + 1) * (rings + 1) + j
                bottom_right = bottom_left + 1

                # Add the first triangle
                indices.append(top_left)
                indices.append(bottom_left)
                indices.append(top_right)

                # Add the second triangle
                indices.append(top_right)
                indices.append(bottom_left)
                indices.append(bottom_right)

        self.indices = np.array(indices, dtype=np.uint32)

    def torus_norm(self, x, y, z, R):
        # Compute the gradient components
        xy_norm = np.sqrt(x**2 + y**2)
        if xy_norm == 0:  # Handle the edge case to avoid division by zero
            raise ValueError("x and y cannot both be zero at the same point.")

        df_dx = 2 * x * (xy_norm - R) / xy_norm
        df_dy = 2 * y * (xy_norm - R) / xy_norm
        df_dz = 2 * z

        # Gradient (normal vector)
        gradient = np.array([df_dx, df_dy, df_dz])

        # Normalize the vector
        norm = np.linalg.norm(gradient)
        normal = gradient / norm if norm != 0 else gradient  # Avoid division by zero

        return normal

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

        self.vao.unbind()
