
from OpenGL.GLU import *
from matrix import *
from shapes import *
from scene import *
from defs import *

class Event:
	def __init__(self):
		self.x = -1
		self.y = -1
		self.button = -1
		self.state = -1
		self.altPressed = False


class View:
	def __init__(self, camera, scene = None):
		self.camera = camera
		self.scene = scene
		self.bgColor = ColorRGBA(0.15, 0.15, 0.15, 1.0)
		self.cameraIsMoving = False
		self.objectAnimOn = False
		self.event = Event()
		self.mouseX = -1
		self.mouseY = -1


	def draw(self):
		glClearColor(0.25, 0.25, 0.25, 1)
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LESS)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.scene.scene_user_info()
		for node in self.scene.nodes:
			node.display(self.camera)
		glutSwapBuffers()


	def setScene(self, scene):
		self.scene = scene


	def setObjectAnim(self, onOff):
		self.objectAnimOn = onOff


	def isObjectAnim(self):
		return self.objectAnimOn


	def setCameraIsMoving(self, onOff):
		self.cameraIsMoving = onOff


	def isCameraMoving(self):
		return self.cameraIsMoving


	# The function called whenever a key is pressed.
	def keyPressed(self, key, x, y):
		# If escape is pressed, kill everything.
		# ord() is needed to get the keycode
		if ord(key) == 27:
			# Escape key = 27
			glutLeaveMainLoop()
			return

		if key == b'f':
			self.camera.reset()
			self.draw()

		if key == b'4':
			for node in self.scene.nodes:
				if not node.fixedDrawStyle:
					node.drawStyle = DrawStyle.WIRE
					node.wireOnShaded = False
					self.draw()

		if key == b'5':
			for node in self.scene.nodes:
				if not node.fixedDrawStyle:
					node.drawStyle = DrawStyle.SMOOTH
					node.wireOnShaded = False
					self.draw()

		if key == b'6':
			for node in self.scene.nodes:
				if not node.fixedDrawStyle and node.drawStyle != DrawStyle.WIRE:
					node.wireOnShaded = True
					self.draw()

		if ord(key) == 43:
			for node in self.scene.nodes:
				node.texVal += 0.1
				if node.texVal > 1:
					node.texVal = 1
			self.draw()

		if ord(key) == 45:
			for node in self.scene.nodes:
				node.texVal -= 0.1
				if node.texVal < 0:
					node.texVal = 0
			self.draw()


	# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
	def resizeView(self, width, height):
		if height == 0:						# Prevent A Divide By Zero If The Window Is Too Small
			height = 1

		glViewport(0, 0, width, height)		# Reset The Current Viewport And Perspective Transformation
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.camera.fov, float(width)/float(height), self.camera.near, self.camera.far)
		glMatrixMode(GL_MODELVIEW)


	# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
	def specialKeyPressed(self, *args):
		if args[0] == GLUT_KEY_LEFT:
			self.camera.eye.x -= .5
			self.camera.center.x -= .5
			self.camera.computeFrame()

		if args[0] == GLUT_KEY_RIGHT:
			self.camera.eye.x += .5
			self.camera.center.x += .5
			self.camera.computeFrame()


	def mousePressed(self, button, state, x, y):
		self.event.x = x
		self.event.y = y
		self.event.state = state
		self.event.button = button

		# get status of alt key
		m = glutGetModifiers()
		self.event.altPressed = m & GLUT_ACTIVE_ALT

		self.mouseX = x
		self.mouseY = y

		if state == 0:
			if self.event.altPressed > 0:
				self.setCameraIsMoving( True )
		else:
			self.setCameraIsMoving( False )


	def mouseMove(self, x, y):
		if self.event.altPressed == False:
			return

		xSpeed = 0.02
		ySpeed = 0.02
		xOffset = (x - self.mouseX) * xSpeed
		yOffset = (y -self.mouseY) * ySpeed

		if ( self.event.button == GLUT_RIGHT_BUTTON ):
			self.camera.zoom(xOffset)
			#self.camera.roll(yOffset)
		elif ( self.event.button == GLUT_MIDDLE_BUTTON ):
			self.camera.dolly(-xOffset, yOffset, 0)
		elif ( self.event.button == GLUT_LEFT_BUTTON ):
			self.camera.yaw(xOffset)
			self.camera.pitch(yOffset)
			#self.camera.dollyCamera(-xOffset, yOffset, 0)

		# store last positions
		self.mouseX = x
		self.mouseY = y

		# remember this point
		self.event.x = x
		self.event.y = y


	# The main drawing function
	def idleFunction(self):
		if self.isObjectAnim() or self.isCameraMoving():
			self.draw()


class Grid(_Shape):
	def __init__(self, name, xSize, zSize):
		vertices = []
		for x in range(-xSize, xSize + 1, 2):
			for z in range(-zSize, zSize + 1, 2):
				vertices.append( Point3f(x, 0, z) )

		faces = []
		for x in range(0, xSize * zSize):
			indexX = x % xSize
			indexZ = x // zSize
			id1 = indexZ * (xSize + 1) + indexX
			id2 = (indexZ + 1) * (xSize + 1) + indexX
			faces.append([id1, id1 + 1, id2 + 1, id2])

		_Shape.__init__(self, name, vertices, faces)

		self.fixedDrawStyle = True

		self.setWireColor(0.3, 0.3, 0.3, 1.0)
		self.xAxisColor = ColorRGBA(0.4, 0.0, 0.0, 1.0)
		self.zAxisColor = ColorRGBA(0.0, 0.4, 0.0, 1.0)
		self.yAxisColor = ColorRGBA(0.0, 0.0, 0.4, 1.0)
		self.axisWidth = 2

		self.originColor = ColorRGBA(0.4, 0.4, 0.4, 1.0)
		self.originRadius = 4

		self.xSize = xSize
		self.zSize = zSize


	def setXAxisColor(self, r, g, b, a):
		self.xAxisColor = ColorRGBA(r, g, b, a)


	def setYAxisColor(self, r, g, b, a):
		self.yAxisColor = ColorRGBA(r, g, b, a)


	def setZAxisColor(self, r, g, b, a):
		self.zAxisColor = ColorRGBA(r, g, b, a)


	def setMainAxisWidth(self, width):
		self.mainAxisWidth = width


	def draw(self):
		# _Shape.draw(self)

		# paint on top
		glDisable(GL_DEPTH_TEST)
		# no lighting
		#glDisable(GL_LIGHTING)

		# draw the main axises wider and in a different color
		glLineWidth(self.axisWidth)

		# draw x axis
		glBegin(GL_LINES)
		glColor3f(self.xAxisColor.r, self.xAxisColor.g, self.xAxisColor.b)
		glVertex3f(-self.xSize, 0, 0)
		glVertex3f(self.xSize, 0, 0)
		glEnd()

		# draw z axis
		glBegin(GL_LINES)
		glColor3f(self.zAxisColor.r, self.zAxisColor.g, self.zAxisColor.b)
		glVertex3f(0, 0, -self.zSize)
		glVertex3f(0, 0, self.zSize)
		glEnd()

		# draw origin
		glPointSize(self.originRadius)

		glBegin(GL_POINTS)
		glColor3f(self.originColor.r, self.originColor.g, self.originColor.b)
		glVertex3f(0, 0, 0)
		glEnd()

		# enaable depth based merge
		glEnable(GL_DEPTH_TEST)
		# enable lighting
		#glEnable(GL_LIGHTING)
