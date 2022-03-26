
from OpenGL.GL import *
from OpenGL.GLUT import *

class Scene:
	def __init__(self):
		self.nodes = []

	def add(self, node):
		self.nodes.append(node)

	def scene_user_info(self):
		glColor3f(1, 1, 0)

		glWindowPos2i(5, 50)
		string = "Press + for increase blend rate. Press - for decrease blend rate."
		for i in string:
			glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(i))

		glWindowPos2i(5, 5)
		string = "Press ESC key to quit."
		for i in string:
			glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(i))
