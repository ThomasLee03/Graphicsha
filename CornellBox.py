"""
Define a fixed scene with rotating lights
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
import math

import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableCube import DisplayableCube
from DisplayableEllipsoid import DisplayableEllipsoid
from DisplayableTorus import DisplayableTorus
from DisplayableCylinder import DisplayableCylinder

class CornellBox(Component, Animation):
    lights = None
    lightCubes = None
    shaderProg = None
    glutility = None

    lRadius = None
    lAngles = None
    lTransformations = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()
        self.shaderProg = shaderProg

         # Room walls
        self.add_wall(Point((-1.5, 0, 0)), (0.1, 3, 3), ColorType.RED)   # Left wall (red)
        self.add_wall(Point((1.5, 0, 0)), (0.1, 3, 3), ColorType.GREEN) # Right wall (green)
        self.add_wall(Point((0, 0, -1.5)), (3, 3, 0.1), ColorType.WHITE) # Back wall (white)
        self.add_wall(Point((0, 1.5, 0)), (3, 0.1, 3), ColorType.WHITE) # Ceiling (white)
        self.add_wall(Point((0, -1.5, 0)), (3, 0.1, 3), ColorType.WHITE) # Floor (white)

        # Light source on ceiling
        lightPos = np.array((0, 1.4, 0))  # Slightly below ceiling
        lightColor = np.array((*ColorType.WHITE, 1.0))
        self.light = Light(lightPos, lightColor)
        self.light.lightOn = True
        self.shaderProg.setLight(0, self.light)

        # Light cube to visualize the light source
        lightCube = Component(Point(lightPos), DisplayableCube(shaderProg, 0.2, 0.1, 0.1, ColorType.WHITE))
        lightCube.renderingRouting = "vertex"
        self.addChild(lightCube)

        # Sphere in the scene
        sphere = Component(Point((-0.6, -1.0, 0.3)), DisplayableEllipsoid(shaderProg, 0.5, 0.5, 0.5, 36, 36))
        sphere.setMaterial(Material(
            np.array((0.1, 0.1, 0.1, 1.0)),
            np.array((0.6, 0.6, 0.6, 1.0)),
            np.array((0.8, 0.8, 0.8, 1.0)), 32
        ))
        sphere.renderingRouting = "lighting"
        self.addChild(sphere)

        # Cube in the scene
        cube = Component(Point((0.6, -1.2, -0.5)), DisplayableCube(shaderProg, 0.4, 0.4, 0.4, ColorType.WHITE))
        cube.setMaterial(Material(
            np.array((0.1, 0.1, 0.1, 1.0)),
            np.array((0.6, 0.6, 0.6, 1.0)),
            np.array((0.8, 0.8, 0.8, 1.0)), 32
        ))
        cube.renderingRouting = "lighting"
        self.addChild(cube)

    def add_wall(self, position, size, color):
        """ Helper method to create and add a wall """
        wall = Component(position, DisplayableCube(self.shaderProg, *size, color))
        wall.renderingRouting = "lighting"
        self.addChild(wall)

    def animationUpdate(self):
        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()


