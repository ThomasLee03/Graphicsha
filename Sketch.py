'''
This is the main entry of your program. Almost all things you need to implement are in this file.
The main class Sketch inherits from CanvasBase. For the parts you need to implement, they are all marked with TODO.
First version Created on 09/28/2018

:author: micou(Zezhou Sun)
:version: 2024.11.11
'''

import os
import math
import time

import numpy as np

import ColorType
from Animation import Animation
from ModelAxes import ModelAxes
from Point import Point
from CanvasBase import CanvasBase
from GLProgram import GLProgram
from GLBuffer import VAO, VBO, EBO, Texture
import GLUtility
from SceneOne import SceneOne
from SceneTwo import SceneTwo
from SceneThree import SceneThree
from CornellBox import CornellBox
try:
    import wx
    from wx import glcanvas
except ImportError:
    raise ImportError("Required dependency wxPython not present")
try:
    # From pip package "Pillow"
    from PIL import Image
except:
    print("Need to install PIL package. Pip package name is Pillow")
    raise ImportError
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


class Sketch(CanvasBase):
    """
    Drawing methods and interrupt methods will be implemented in this class.
    
    Variable Instruction:
        * debug(int): Define debug level for log printing

        * 0 for stable version, minimum log is printed
        * 1 will print general logs for lines and triangles
        * 2 will print more details and do some type checking, which might be helpful in debugging

        
    Method Instruction:
        
        
    Here are the list of functions you need to override:
        * Interrupt_MouseL: Used to deal with mouse click interruption. Canvas will be refreshed with updated buff
        * Interrupt_MouseLeftDragging: Used to deal with mouse dragging interruption.
        * Interrupt_Keyboard: Used to deal with keyboard press interruption. Use this to add new keys or new methods
        
    Here are some public variables in parent class you might need:
        
        
    """
    context = None

    debug = 1

    last_mouse_leftPosition = None
    last_mouse_middlePosition = None
    components = None
    
    # Image mode
    ImageModeOn = False
    start_time = None
    left_mouse_down = 0

    texture = None
    shaderProg = None
    glutility = None

    frameCount = 0

    lookAtPt = None
    upVector = None
    backgroundColor = None
    # use these three to control camera position, mainly used in mouse dragging
    cameraDis = None
    cameraTheta = None  # theta on horizontal sphere cut, in range [0, 2pi]
    cameraPhi = None  # in range [-pi, pi], for smooth purpose

    viewMat = None
    perspMat = None

    pauseScene = False

    # models
    basisAxes = None
    scene = None

    # If you are having trouble rotating the camera, try increasing this parameter
    # (Windows users with trackpads may need this)
    MOUSE_ROTATE_SPEED = 1
    MOUSE_SCROLL_SPEED = 2.5

    ambientOn= False
    diffuseOn = False
    specularOn = False

    light1On = True
    light2On = True
    light3On = True
    light4On = True


    

    def __init__(self, parent):
        """
        Init everything. You should set your model here.
        """
        super(Sketch, self).__init__(parent)
        # prepare OpenGL context
        contextAttrib = glcanvas.GLContextAttrs()
        contextAttrib.PlatformDefaults().CoreProfile().MajorVersion(3).MinorVersion(3).EndList()
        self.context = glcanvas.GLContext(self, ctxAttrs=contextAttrib)
        # Initialize Parameters
        self.last_mouse_leftPosition = [0, 0]
        self.last_mouse_middlePosition = [0, 0]
        self.components = []
        self.backgroundColor = ColorType.BLUEGREEN
        self.light1On = True
        self.light2On = True
        self.light3On = True

        


        # Image mode settings
        self.start_time = time.time()

        # add components to top level
        self.resetView()

        self.glutility = GLUtility.GLUtility()

    def resetView(self):
        self.lookAtPt = [0, 0, 0]
        self.upVector = [0, 1, 0]
        self.cameraDis = 6
        self.cameraPhi = math.pi / 6
        self.cameraTheta = math.pi / 2

    def switchScene(self, scene):
        self.scene = scene
        self.topLevelComponent.clear()
        self.topLevelComponent.addChild(self.scene)
        self.topLevelComponent.initialize()

    def InitGL(self):
        self.shaderProg = GLProgram()
       # self.shaderProg.compile()

        try:
            self.shaderProg.compile()
        except Exception as e:
            print("Fragment Shader Source:\n", self.shaderProg.fragmentShaderSource)
            raise e

        self.shaderProg.setBool("light[0].pointOn", self.light1On)

        self.shaderProg.setBool("light[1].pointOn", self.light1On)
        # instantiate models, then can only be done with a compiled GL program
        self.basisAxes = ModelAxes(self.shaderProg, Point((0, 0, 0)))
        self.basisAxes.initialize()
        self.shaderProg.setBool("ambientOn", self.ambientOn)
        self.shaderProg.setBool("diffuseOn", self.diffuseOn)
        self.shaderProg.setBool("specularOn", self.specularOn)

        self.switchScene(SceneThree(self.shaderProg))

        gl.glClearColor(*self.backgroundColor, 1.0)
        gl.glClearDepth(1.0)
        gl.glViewport(0, 0, self.size[0], self.size[1])

        # enable depth checking
        gl.glEnable(gl.GL_DEPTH_TEST)

        # set basic viewing matrix
        self.perspMat = self.glutility.perspective(45, self.size.width, self.size.height, 0.01, 100)
        self.shaderProg.setMat4("projectionMat", self.perspMat)
        self.shaderProg.setMat4("viewMat", self.glutility.view(self.getCameraPos(), self.lookAtPt, self.upVector))
        self.shaderProg.setMat4("modelMat", np.identity(4))
        self.shaderProg.setVec3("viewPosition", np.array(self.getCameraPos()))
        self.shaderProg.setBool("imageFlag", self.ImageModeOn)

    def getCameraPos(self):
        ct = math.cos(self.cameraTheta)
        st = math.sin(self.cameraTheta)
        cp = math.cos(self.cameraPhi)
        sp = math.sin(self.cameraPhi)
        result = [self.lookAtPt[0] + self.cameraDis * ct * cp,
                  self.lookAtPt[1] + self.cameraDis * sp,
                  self.lookAtPt[2] + self.cameraDis * st * cp]
        return result

    def OnResize(self, event):
        contextAttrib = glcanvas.GLContextAttrs()
        contextAttrib.PlatformDefaults().CoreProfile().MajorVersion(3).MinorVersion(3).EndList()
        self.context = glcanvas.GLContext(self, ctxAttrs=contextAttrib)
        self.size = self.GetClientSize()
        self.size[1] = max(1, self.size[1])  # avoid divided by 0
        self.SetCurrent(self.context)

        self.init = False
        self.Refresh(eraseBackground=True)
        self.Update()

    def OnPaint(self, event=None):
        """
        This will be called at every frame
        """
        self.SetCurrent(self.context)
        if not self.init:
            # Init the OpenGL environment if not initialized
            self.InitGL()
            self.init = True
        # the draw method
        self.OnDraw()

    def OnDraw(self):
        gl.glClearColor(*self.backgroundColor, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.viewMat = self.glutility.view(self.getCameraPos(), self.lookAtPt, self.upVector)
        self.shaderProg.setMat4("viewMat", self.viewMat)
        self.shaderProg.setVec3("viewPosition", np.array(self.getCameraPos()))
        if self.ImageModeOn:
            self.shaderProg.setVec3("iResolution", np.array((float(self.size.width), float(self.size.height), 1.0)))
            self.shaderProg.setVec3("iMouse", np.array((float(self.last_mouse_leftPosition[0]), float(self.last_mouse_leftPosition[1]), float(self.left_mouse_down))))
            self.shaderProg.setFloat("iTime", time.time() - self.start_time)

        if not self.pauseScene and isinstance(self.scene, Animation):
            self.scene.animationUpdate()
        self.topLevelComponent.update(np.identity(4))
        self.topLevelComponent.draw(self.shaderProg)

        # draw the axes on the canvas bottom right corner
        resultPt = self.unprojectCanvas(0.9 * self.size[0], 0.1 * self.size[1], 0.3)
        self.basisAxes.setCurrentPosition(resultPt)
        self.basisAxes.draw(self.shaderProg)

        self.SwapBuffers()

    def OnDestroy(self, event):
        """
        Window destroy event binding

        :param event: Window destroy event
        :return: None
        """
        if self.shaderProg is not None:
            del self.shaderProg
        super(Sketch, self).OnDestroy(event)

    def Interrupt_Scroll(self, wheelRotation):
        """
        When mouse wheel rotating detected, do following things

        :param wheelRotation: mouse wheel changes, normally +120 or -120
        :return: None
        """
        if wheelRotation == 0:
            return
        wheelChange = wheelRotation / abs(wheelRotation)
        self.cameraDis = max(self.cameraDis - wheelChange * 0.1, 0.01)
        self.update()

    def unprojectCanvas(self, x, y, u=0.5):
        """
        unproject a canvas point to world coordiantes. 2D -> 3D
        you need give an extra parameter u, to tell the method how far are you from znear
        u is the proportion of distance to znear / zfar-znear
        in the gluUnProject, the distribution of z is not linear when using perspective projection,
        so z=0.5 is not in the middle,
        that's why we compute out the ray and use linear interpolation and u to get the point

        :param u: u is the proportion to the znear/, in range [0, 1]
        :type u: float
        """
        result1 = self._unproject(x, y, 0.0)
        result2 = self._unproject(x, y, 1.0)
        result = Point([(1 - u) * r1 + u * r2 for r1, r2 in zip(result1, result2)])
        return result

    def _unproject(self, x, y, z):
        model_matrix = np.identity(4)
        proj_matrix = self.viewMat @ self.perspMat
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        model_view_proj_matrix = proj_matrix @ model_matrix
        inv_model_view_proj_matrix = np.linalg.inv(model_view_proj_matrix)

        x_ndc = (x - viewport[0]) / viewport[2] * 2.0 - 1.0
        y_ndc = (y - viewport[1]) / viewport[3] * 2.0 - 1.0
        z_ndc = 2.0 * z - 1.0
        
        ndc_coords = np.array([x_ndc, y_ndc, z_ndc, 1.0])
        world_coords = inv_model_view_proj_matrix.T @ ndc_coords # transpose because they are row-major
        if world_coords[3] != 0:
            world_coords /= world_coords[3]
        return world_coords[:3]

    def Interrupt_MouseL(self, x, y):
        """
        When mouse click detected, store current position in last_mouse_leftPosition

        :param x: Mouse click's x coordinate
        :type x: int
        :param y: Mouse click's y coordinate
        :type y: int
        :return: None
        """
        self.last_mouse_leftPosition[0] = x
        self.last_mouse_leftPosition[1] = y
        self.left_mouse_down = 0

    def Interrupt_MouseMiddleDragging(self, x, y):
        """
        When mouse drag motion with middle key detected, interrupt with new mouse position

        :param x: Mouse drag new position's x coordinate
        :type x: int
        :param y: Mouse drag new position's x coordinate
        :type y: int
        :return: None
        """

        if self.new_dragging_event:
            self.last_mouse_middlePosition[0] = x
            self.last_mouse_middlePosition[1] = y
            return

        originalMidPt = self.unprojectCanvas(*self.last_mouse_middlePosition, 0.5)

        self.last_mouse_middlePosition[0] = x
        self.last_mouse_middlePosition[1] = y

        currentMidPt = self.unprojectCanvas(x, y, 0.5)
        changes = currentMidPt - originalMidPt
        moveSpeed = 0.185 * self.cameraDis / 6
        self.lookAtPt = [self.lookAtPt[0] - changes[0] * moveSpeed,
                         self.lookAtPt[1] - changes[1] * moveSpeed,
                         self.lookAtPt[2] - changes[2] * moveSpeed]

    def Interrupt_MouseLeftDragging(self, x, y):
        """
        When mouse drag motion detected, interrupt with new mouse position

        :param x: Mouse drag new position's x coordinate
        :type x: int
        :param y: Mouse drag new position's x coordinate
        :type y: int
        :return: None
        """
        if self.new_dragging_event:
            self.left_mouse_down = 1
            self.last_mouse_leftPosition[0] = x
            self.last_mouse_leftPosition[1] = y
            return

        # Change viewing angle when dragging happened
        dx = x - self.last_mouse_leftPosition[0]
        dy = y - self.last_mouse_leftPosition[1]

        # restrict phi movement range, stop cameraphi changes at pole points
        self.cameraPhi = min(math.pi / 2, max(-math.pi / 2, self.cameraPhi - dy / 50))
        self.cameraTheta += dx / 100 * (self.MOUSE_ROTATE_SPEED)

        self.cameraTheta = self.cameraTheta % (2 * math.pi)

        self.last_mouse_leftPosition[0] = x
        self.last_mouse_leftPosition[1] = y

    def update(self):
        """
        Update current canvas
        :return: None
        """
        self.topLevelComponent.update(np.identity(4))

    def Interrupt_Keyboard(self, keycode):
        """
        Keyboard interrupt bindings

        :param keycode: wxpython keyboard event's keycode
        :return: None
        """

        if keycode in [wx.WXK_RETURN]:
            self.update()
        if keycode in [wx.WXK_LEFT]:
            self.update()
        if keycode in [wx.WXK_RIGHT]:
            self.update()
        if keycode in [wx.WXK_UP]:
            self.Interrupt_Scroll(1)
            self.update()
        if keycode in [wx.WXK_DOWN]:
            self.Interrupt_Scroll(-1)
            self.update()
        if chr(keycode) in "rR":
            # reset viewing angle only
            self.resetView()
        if chr(keycode) in "pP":
            self.pauseScene = not self.pauseScene
        if chr(keycode) in "iI":
            self.ImageModeOn = not self.ImageModeOn
            self.shaderProg.setBool("imageFlag", self.ImageModeOn)
        if chr(keycode) in "aA":
            self.ambientOn = not self.ambientOn
            self.shaderProg.setBool("ambientOn", self.ambientOn)
            self.update()
        if chr(keycode) in "dD":
            self.diffuseOn = not self.diffuseOn
            self.shaderProg.setBool("diffuseOn", self.diffuseOn)
            self.update()
        if chr(keycode) in "sS":
            self.specularOn = not self.specularOn
            self.shaderProg.setBool("specularOn", self.specularOn)
            self.update()

        if chr(keycode) in "9":
            self.switchScene(SceneOne(self.shaderProg))
            self.update()
        if chr(keycode) in "8":
            self.switchScene(SceneTwo(self.shaderProg))
            self.update()
        if chr(keycode) in "7":
            self.switchScene(SceneThree(self.shaderProg))
            self.update()
        if chr(keycode) in "6":
            self.switchScene(CornellBox(self.shaderProg))
            self.update()
            
        if chr(keycode) == '1':
            self.light1On = not self.light1On
            self.scene.lights[0].lightOn = self.light1On
            self.shaderProg.setBool("light[0].lightOn", self.light1On)
            print(f"Light 1 {'ON' if self.light1On else 'OFF'} {self.scene.lights[0].lightType}")
            self.update()
        # Toggle Light 2
        if chr(keycode) == '2':
            self.light2On = not self.light2On
            self.scene.lights[1].lightOn = self.light2On
            self.shaderProg.setBool("light[1].lightOn", self.light2On)
            print(f"Light 2 {'ON' if self.light2On else 'OFF'}{self.scene.lights[1].lightType}")
            self.update()

        # Toggle Light 3
        if chr(keycode) == '3':
            self.scene.lights[2].lightOn = not self.scene.lights[2].lightOn
            self.shaderProg.setBool("light[2].pointOn", self.scene.lights[2].lightOn)
            print(f"Light 3 {'ON' if self.light3On else 'OFF'}{self.scene.lights[2].lightType}")
            self.update()
        # Toggle Light 4
        if chr(keycode) == '4':
            self.light4On = not self.light4On
            self.scene.lights[3].lightOn = self.light4On
            self.shaderProg.setBool("light[2].pointOn", self.light4On)
            print(f"Light 4 {'ON' if self.light4On else 'OFF'}")
            self.update()
            

        # TODO 4.2 is at here
        # TODO 5.3 is at here


if __name__ == "__main__":
    print("This is the main entry! ")
    app = wx.App(False)
    # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame, here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
    # Resize disabled in this one
    frame = wx.Frame(None, size=(500, 500), title="Test",
                     style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)  # Disable Resize: ^ wx.RESIZE_BORDER
    canvas = Sketch(frame)

    frame.Show()
    app.MainLoop()
