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

class SceneTwo(Component, Animation):
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

        # Table
        table = Component(Point((0, -0.5, 0)), DisplayableCube(shaderProg, 4, 0.2, 2))
        table.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.6, 0.4, 0.2, 1.0)),  # Wood color
            specular=np.array((0.3, 0.3, 0.3, 1.0)),
            highlight=16
        ))
        table.renderingRouting = "lighting"
        self.addChild(table)

        # Lamp
        lampBase = Component(Point((1.5, -0.4, 0)), DisplayableCube(shaderProg, 0.3, 0.1, 0.3))
        lampBase.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.4, 0.4, 0.4, 1.0)),  # Metal
            specular=np.array((0.7, 0.7, 0.7, 1.0)),
            highlight=64
        ))
        lampBase.renderingRouting = "lighting"
        self.addChild(lampBase)

        lampStand = Component(Point((1.5, 0.1, 0)), DisplayableCylinder(shaderProg, 0.1, 0.7, 36))
        lampStand.setDefaultAngle(90,lampStand.uAxis)
        lampStand.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.6, 0.6, 0.6, 1.0)),  # Metal
            specular=np.array((0.8, 0.8, 0.8, 1.0)),
            highlight=64
        ))
        lampStand.renderingRouting = "lighting"
        self.addChild(lampStand)

        lampShade = Component(Point((1.5, 0.2, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.3, 0.5, 36, 36))
        lampShade.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.8, 0.6, 0.6, 1.0)),  # Plastic
            specular=np.array((0.9, 0.9, 0.9, 1.0)),
            highlight=32
        ))
        lampShade.renderingRouting = "lighting"
        self.addChild(lampShade)

        # computer
        computerbase = Component(Point((-1, -0.4, 0)), DisplayableCube(shaderProg, 1.2, 0.2, 1.2))
        computerbase.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.6, 0.4, 0.2, 1.0)),  # Wood
            specular=np.array((0.3, 0.3, 0.3, 1.0)),
            highlight=16
        ))
        computerbase.renderingRouting = "lighting"
        self.addChild(computerbase)

        computerback = Component(Point((-1, 0.2, -0.6)), DisplayableCube(shaderProg, 1.2, 1.0, 0.2))
        computerback.setMaterial(Material(
            ambient=np.array((0.02, 0.02, 0.02, .010)),
            diffuse=np.array((0.6, 0.4, 0.2, 1.0)),  # Wood
            specular=np.array((0.3, 0.3, 0.3, 1.0)),
            highlight=16
        ))
        computerback.renderingRouting = "lighting"
        self.addChild(computerback)
        #block = Component(Point((1.5, -0.3, 0)), DisplayableCube(shaderProg, 2, .1, 0.1))
        #self.addChild(block)
        # Lights
        self.lights = [
            Light(position=np.array((1.5, .1, 0)), color=np.array((1.0, 1.0, 0.8, 1.0)), lightType="point", spotRadialFactor=np.array((.1, 0.1, 0.01))),  # Lamp light
            Light(position=np.array((0, 1, 1)), color=np.array((1.0, 1.0, 1.0, 1.0)), lightType="infinite", infiniteDirection=np.array((0, -1, 0))),  # Sunlight
            Light(position=np.array((1.5, .1, 0)), color=np.array((1.0, 0.5, 0.5, 1.0)), lightType="spot", spotDirection=np.array((0, -1, 0)), spotAngleLimit=1, spotRadialFactor=np.array((.1, 0.1, 0.1)))  # Spotlight
        ]

    def lightPos(self, radius, thetaAng, transformationMatrix):
        r = np.zeros(4)
        r[0] = radius * math.cos(thetaAng / 180 * math.pi)
        r[2] = radius * math.sin(thetaAng / 180 * math.pi)
        r[3] = 1
        r = transformationMatrix @ r
        return r[0:3]
    
    

    def animationUpdate(self):
        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
