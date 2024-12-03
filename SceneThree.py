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

class SceneThree(Component, Animation):
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

        fixedPositions = [
            Point((1, .9, 1)),  
            Point((0, 1.4, 0)), 
            Point((0, -4, 0))
        ]

        #materials

        among_us_material = Material(
            ambient=np.array([0.3, 0.3, 0.1, 1.0]),  # Slight ambient contribution
            diffuse=np.array([0.1, 0.1, 0.1, 1.0]),  # Vibrant red color (adjust as needed)
            specular=np.array([0.5, 0.5, 0.5, 1.0]),  # Moderate shininess for highlights
            highlight=32  # Medium shininess (Phong highlight size)
        )

        among_us_material_2 = Material(
            ambient=np.array([0.3, 0.1, 0.3, 1.0]),  # Slight ambient contribution
            diffuse=np.array([0.1, 0.1, 0.1, 1.0]),  # Vibrant red color (adjust as needed)
            specular=np.array([0.5, 0.5, 0.5, 1.0]),  # Moderate shininess for highlights
            highlight=32  # Medium shininess (Phong highlight size)
        )

        among_us_material_3 = Material(
            ambient=np.array([0.1, 0.3, 0.3, 1.0]),  # Slight ambient contribution
            diffuse=np.array([0.1, 0.1, 0.1, 1.0]),  # Vibrant red color (adjust as needed)
            specular=np.array([0.5, 0.5, 0.5, 1.0]),  # Moderate shininess for highlights
            highlight=32  # Medium shininess (Phong highlight size)
        )
        
        wood_material = Material(
            ambient=np.array([0.3, 0.2, 0.1, 1.0]),  # Warm ambient tones for wood
            diffuse=np.array([0.6, 0.4, 0.2, 1.0]),  # Main brownish tone
            specular=np.array([0.2, 0.2, 0.2, 1.0]),  # Subtle highlights for polished look
            highlight=16  # Slightly rougher shininess
        )

        shiny_material = Material(
            ambient=np.array([0.1, 0.1, 0.1, 1.0]),  # Minimal ambient contribution
            diffuse=np.array([0.6, 0.6, 0.6, 1.0]),  # Neutral gray for base color
            specular=np.array([1.0, 1.0, 1.0, 1.0]),  # Strong white highlights for high reflectivity
            highlight=128  # Very sharp and glossy shininess
        )


        #table
        cube = Component(Point((0, -.45, 0)), DisplayableCube(shaderProg, 2, 1, 2))
        cube.setMaterial(wood_material)
        cube.renderingRouting = "lighting"
        self.addChild(cube)


        #among us ONE
        
        # Main Body
        body = Component(Point((0, 0, -1.7)), DisplayableEllipsoid(shaderProg, 0.5, 0.8, 0.5, 36, 36))
        body.renderingRouting = "lighting"
        self.addChild(body)
        body.setMaterial(among_us_material)
        # Left Leg
        left_leg = Component(Point((-0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        left_leg.renderingRouting = "lighting"
        body.addChild(left_leg)
        left_leg.setMaterial(among_us_material)
        # Right Leg
        right_leg = Component(Point((0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        right_leg.renderingRouting = "lighting"
        body.addChild(right_leg)
        right_leg.setMaterial(among_us_material)
        # Backpack
        backpack = Component(Point((0, 0.1, -0.4)), DisplayableCylinder(shaderProg, 0.2, 0.6, 36, 36))
        backpack.setDefaultAngle(90, backpack.uAxis)
        backpack.renderingRouting = "lighting"
        body.addChild(backpack)
        backpack.setMaterial(among_us_material)


        #among us TWO
        # Main Body
        body = Component(Point((-1.7, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.8, 0.5, 36, 36))
        body.renderingRouting = "lighting"
        body.setDefaultAngle(90, backpack.vAxis)
        self.addChild(body)
        body.setMaterial(among_us_material_2)
        # Left Leg
        left_leg = Component(Point((-0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        left_leg.renderingRouting = "lighting"
        body.addChild(left_leg)
        left_leg.setMaterial(among_us_material_2)
        # Right Leg
        right_leg = Component(Point((0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        right_leg.renderingRouting = "lighting"
        body.addChild(right_leg)
        right_leg.setMaterial(among_us_material_2)
        # Backpack
        backpack = Component(Point((0, 0.1, -0.4)), DisplayableCylinder(shaderProg, 0.2, 0.6, 36, 36))
        backpack.setDefaultAngle(90, backpack.uAxis)
        backpack.renderingRouting = "lighting"
        body.addChild(backpack)
        backpack.setMaterial(among_us_material_2)
        # Visor
        visor = Component(Point((0, 0.4, 0.4)), DisplayableEllipsoid(shaderProg, 0.3, 0.2, 0.1, 36, 36))
        visor.renderingRouting = "lighting"
        body.addChild(visor)
        visor.setMaterial(shiny_material)

        #among us THREE
        # Main Body
        body = Component(Point((1.7, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.8, 0.5, 36, 36))
        body.renderingRouting = "lighting"
        body.setDefaultAngle(-90, backpack.vAxis)
        self.addChild(body)
        body.setMaterial(among_us_material_3)
        # Left Leg
        left_leg = Component(Point((-0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        left_leg.renderingRouting = "lighting"
        body.addChild(left_leg)
        left_leg.setMaterial(among_us_material_3)
        # Right Leg
        right_leg = Component(Point((0.2, -0.8, 0)), DisplayableCube(shaderProg, 0.2, 0.4, 0.2))
        right_leg.renderingRouting = "lighting"
        body.addChild(right_leg)
        right_leg.setMaterial(among_us_material_3)
        # Backpack
        backpack = Component(Point((0, 0.1, -0.4)), DisplayableCylinder(shaderProg, 0.2, 0.6, 36, 36))
        backpack.setDefaultAngle(90, backpack.uAxis)
        backpack.renderingRouting = "lighting"
        body.addChild(backpack)
        backpack.setMaterial(among_us_material_3)
        visor = Component(Point((0, 0.4, 0.4)), DisplayableEllipsoid(shaderProg, 0.3, 0.2, 0.1, 36, 36))
        visor.renderingRouting = "lighting"
        body.addChild(visor)
        visor.setMaterial(shiny_material)

        buttonbox = Component(Point((0, .1, 0)), DisplayableCube(shaderProg, .5, .1, .5))
        buttonbox.setMaterial(shiny_material)
        buttonbox.renderingRouting = "lighting"
        self.addChild(buttonbox)


        button = Component(Point((0, .15, 0)), DisplayableCylinder(shaderProg, 0.2, .2))
        button.setMaterial(shiny_material)
        button.setDefaultAngle(90, button.uAxis)
        button.renderingRouting = "lighting"
        buttonbox.addChild(button)
        positioneye = Point((0,0.4,-1.3))
        l0 = Light(
            position=positioneye,  # Position of the light
            color=np.array((*ColorType.GREEN, 1.0)),  # Light color
            spotRadialFactor=np.array((1.0, 0.1, 1)),  # Radial attenuation factors
            lightType="point"  # Specify that this is a point light
        )
        lightCube0 = Component(positioneye, DisplayableEllipsoid(shaderProg, 0.3, 0.2, 0.1, 36, 36, ColorType.GREEN))
        
        lightCube0.renderingRouting = "vertex" # Spotlight

        l1 = Light(
            position=fixedPositions[1],  # Position of the light
            color=np.array((*ColorType.RED, 1.0)),  # Light color
            spotDirection=np.array((0, -1, 0)),  # Spotlight direction (downward) 
            spotRadialFactor=np.array((.1, 0.1, 0.01)),  # Radial attenuation factors
            spotAngleLimit=.4,  # Spotlight cone angle limit in degrees
            lightType="spot"  # Specify that this is a spotlight
        )
        lightCube1 = Component(fixedPositions[1], DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.RED))
        lightCube1.renderingRouting = "vertex"
        l2 = Light(
            position=fixedPositions[2],  # Position of the light
            color=np.array((*ColorType.SOFTBLUE, 1.0)),  # Light color
            infiniteDirection=np.array((0, 1, 0)),  # Infinite light direction (e.g., pointing forward)
            lightType="infinite"  # Specify that this is an infinite light
        )
        lightCube2 = Component(fixedPositions[2], DisplayableCube(shaderProg, 5, .2, 5, ColorType.SOFTBLUE))
        lightCube2.renderingRouting = "vertex"

        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.lights = [l0, l1, l2]
        self.lightCubes = [lightCube0, lightCube1, lightCube2]
    def animationUpdate(self):
        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
