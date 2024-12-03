"""
Define a class to store light information
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

import numpy as np

from Point import Point


class Light:
    position = None
    color = None

    infiniteOn = False
    infiniteDirection = None

    spotOn = False
    spotDirection = None
    spotRadialFactor = None
    spotAngleLimit = 0.0

    pointOn = False

    lightOn = True

    lightType = ""

    def __init__(self, position=None, color=None, infiniteDirection=None, spotDirection=None, spotRadialFactor=None, spotAngleLimit=0, lightType="point"):
        # set basic light
        
        self.lightOn =True
        if position is not None:
            self.setPosition(position)
        else:
            self.position = np.array((0, 0, 0))

        if color is not None:
            self.setColor(color)
        else:
            self.color = np.array((0, 0, 0, 0))
        # init radial attenuation parameters
        if infiniteDirection is not None and lightType == "infinite":
            self.infiniteOn = True
            self.setInfiniteDirection(infiniteDirection)
            self.lightType = lightType
        else:
            self.radialOn = False
            self.infiniteDirection = np.array((0, 0, 0))

        # init spot light parameters
        if spotDirection is not None and lightType == "spot":
            self.spotOn = True
            self.setSpotDirection(spotDirection)
            self.setSpotRadialFactor(spotRadialFactor if (spotDirection is not None) else np.array((0, 0, 0)))
            self.setSpotAngleLimit(spotAngleLimit)
            self.spotAngleLimit = spotAngleLimit
            self.lightType = lightType
        else:
            self.spotOn = False
            self.spotDirection = np.array((0, 0, 0))
            self.spotRadialFactor = np.array((0, 0, 0))

        if spotRadialFactor is not None and lightType == "point":
            self.setSpotRadialFactor(spotRadialFactor)
            self.lightType = lightType
            self.pointOn = True
        

    def __repr__(self):
        return f"pos: {self.position}, color:{self.color},\
        {self.infiniteOn},{self.infiniteDirection},\
        {self.spotOn},{self.spotDirection}, {self.spotRadialFactor},{self.spotAngleLimit}, {self.pointOn}, {self.lightOn}"

    def setColor(self, color):
        if (not isinstance(color, np.ndarray)) or color.size != 4:
            raise TypeError("color must be a size 4 ndarray")
        self.color = color

    def setPosition(self, position):
        if (not isinstance(position, np.ndarray)) and (not isinstance(position, Point)):
            raise TypeError("position must be ndarray/Point")
        if isinstance(position, np.ndarray):
            if position.size != 3:
                raise TypeError("position must be a size 3 ndarray")
            self.position = position
        if isinstance(position, Point):
            if position.coords.size != 3:
                raise TypeError("position must be a size 3 Point")
            self.position = position.coords

    def setInfiniteDirection(self, infiniteDirection):
        if (not isinstance(infiniteDirection, np.ndarray)) and (not isinstance(infiniteDirection, Point)):
            raise TypeError("infiniteDirection must be ndarray/Point")
        if isinstance(infiniteDirection, np.ndarray):
            if infiniteDirection.size != 3:
                raise TypeError("infiniteDirection must be a size 3 ndarray")
            self.infiniteDirection = infiniteDirection
        if isinstance(infiniteDirection, Point):
            if infiniteDirection.coords.size != 3:
                raise TypeError("infiniteDirection must be a size 3 Point")
            self.infiniteDirection = infiniteDirection.coords
        self.infiniteOn = True

    def setSpotRadialFactor(self, spotRadialFactor):
        if (not isinstance(spotRadialFactor, np.ndarray)) or spotRadialFactor.size != 3:
            raise TypeError("spotRadialFactor must be a size 3 ndarray")
        self.spotRadialFactor = spotRadialFactor

    def setSpotAngleLimit(self, spotAngleLimit):
        if not type(spotAngleLimit) in [int, float]:
            raise TypeError("spotAngleLimit must be a int/float")
        self.spotAngleLimit = spotAngleLimit

    def setSpotDirection(self, spotDirection):
        if (not isinstance(spotDirection, np.ndarray)) and (not isinstance(spotDirection, Point)):
            raise TypeError("spotDirection must be ndarray/Point")
        if isinstance(spotDirection, np.ndarray):
            if spotDirection.size != 3:
                raise TypeError("spotDirection must be a size 3 ndarray")
            self.spotDirection = spotDirection
        if isinstance(spotDirection, Point):
            if spotDirection.coords.size != 3:
                raise TypeError("spotDirection must be a size 3 Point")
            self.spotDirection = spotDirection.coords
        self.spotOn = True
