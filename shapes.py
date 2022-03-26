
import random
from boundingbox import *
from defs import DrawStyle
from shader import *
from program import Program
from fileIO import FileIO
from PIL import Image
import numpy

__all__ = ['_Shape', 'Cube', 'DrawStyle']

class _Shape:
	def __init__(self, name, vertices, faces, text_coords, vector_normals):
		self.vertices = vertices
		self.edges = []
		self.faces = faces
		self.colors = []
		self.obj2World = Matrix()
		self.drawStyle = DrawStyle.NODRAW
		self.wireOnShaded = False
		self.wireWidth = 2
		self.name = name
		self.fixedDrawStyle = False
		self.wireColor = ColorRGBA(0.7, 1.0, 0.0, 1.0)
		self.wireOnShadedColor = ColorRGBA(1.0, 1.0, 1.0, 1.0)
		self.bboxObj = BoundingBox()
		self.bboxWorld = BoundingBox()
		self.calcBboxObj()

		self.uvs = text_coords
		self.vector_normals = vector_normals

		self.program = None		 # Program object
		self.VAO = None
		self.VBO = None
		self.VBOData = None
		self.position = Point3f(0, 0, 0)
		self.nVertices = 0
		self.tex1_ID = None
		self.tex2_ID = None
		self.texVal = 0
		self.startProgram()


	def calcBboxObj(self):
		for vertex in self.vertices:
			self.bboxObj.expand(vertex)

	def startProgram(self):
		self.initialize_program()
		self.init_vertex_buffer_data()
		self.init_vertex_buffer()
		self.initTexture("./textures/texture1.png", "./textures/texture2.png")

	def setDrawStyle(self, style):
		self.drawStyle = style

	def setWireColor(self, r, g, b, a):
		self.wireColor = ColorRGBA(r, g, b, a)

	def setWireWidth(self, width):
		self.wireWidth = width

	def display(self, camera):
		# use our program
		from matrix import Matrix
		glUseProgram(self.program.program_ID)

		value = glGetUniformLocation(self.program.program_ID, "value")
		glUniform1f(value, self.texVal)

		# get matrices and bind them to vertex shader locations
		modelLocation = glGetUniformLocation(self.program.program_ID, "model")
		glUniformMatrix4fv(modelLocation, 1, GL_FALSE, Matrix.get_model_matrix(self.position))

		viewLocation = glGetUniformLocation(self.program.program_ID, "view")
		glUniformMatrix4fv(viewLocation, 1, GL_FALSE, Matrix.get_view_matrix(camera))
		projLocation = glGetUniformLocation(self.program.program_ID, "proj")
		glUniformMatrix4fv(projLocation, 1, GL_FALSE, Matrix().getProjMatrix(camera.getNear(),
																			 camera.getFar(),
																			 camera.getFov()))
		# bind to our VAO
		glBindVertexArray(self.VAO)
		# draw stuff
		glDrawArrays(GL_QUADS, 0, self.nVertices)
		# reset to defaults
		glBindVertexArray(0)
		glUseProgram(0)

	def Translate(self, x, y, z):
		self.position = self.position.__add__(Point3f(x, y, z))

	def initialize_program(self):
		shader = Shader()
		shader_list = shader.shader_list

		shader_list.append(Shader.create_shader(GL_VERTEX_SHADER, FileIO.read_shader_file("./shaders/vertexShader.vert")))
		shader_list.append(Shader.create_shader(GL_FRAGMENT_SHADER, FileIO.read_shader_file("./shaders/fragShader.frag")))

		self.program = _Shape.create_program(shader_list)

		for shader in shader_list:
			glDeleteShader(shader)

	def init_vertex_buffer_data(self):
		faces = self.faces

		finalVertexPositions = []
		finalVertexColors = []
		finalVertexUvs = []
		finalVertexNormals = []

		# go over faces and assemble an array for all vertex data
		faceID = 0
		for face in faces:
			for vertex in face:
				finalVertexPositions.extend(self.vertices[vertex[0]].convert_to_array())
				finalVertexColors.extend([1, 1, 1, 1.0])
				finalVertexUvs.extend(self.uvs[vertex[1]])
				finalVertexNormals.extend(self.vector_normals[vertex[2]].convert_to_array())

			faceID += 1

		self.VBOData = numpy.array(finalVertexPositions + finalVertexColors + finalVertexUvs, dtype='float32')

	def init_vertex_buffer(self):
		vertexDim = 4
		# nVertices = len(self.faces) * vertexDim
		self.nVertices = len(self.faces) * vertexDim

		self.VAO = glGenVertexArrays(1)
		self.VBO = glGenBuffers(1)

		# bind to our VAO
		glBindVertexArray(self.VAO)

		# now change the state - it will be recorded in the VAO
		# set array buffer to our ID
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		elementSize = numpy.dtype(numpy.float32).itemsize

		# third argument is criptic - in c_types if you multiply a data type with an integer you create an array of that type
		glBufferData(GL_ARRAY_BUFFER,
					 len(self.VBOData) * elementSize,
					 self.VBOData,
					 GL_STATIC_DRAW
					 )

		# setup vertex attributes
		offset = 0

		# location 0
		glVertexAttribPointer(0, vertexDim, GL_FLOAT, GL_FALSE, elementSize * vertexDim, ctypes.c_void_p(offset))
		glEnableVertexAttribArray(0)

		# define colors which are passed in location 1 - they start after all positions and has four floats consecutively
		offset += elementSize * vertexDim * self.nVertices
		glVertexAttribPointer(1, vertexDim, GL_FLOAT, GL_FALSE, elementSize * vertexDim, ctypes.c_void_p(offset))
		glEnableVertexAttribArray(1)

		offset += elementSize * vertexDim * self.nVertices
		glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, elementSize * 2, ctypes.c_void_p(offset))
		glEnableVertexAttribArray(2)

		# reset array buffers
		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindVertexArray(0)

	def initTexture(self, tex1FileName, tex2FileName):
		glUseProgram(self.program.program_ID)

		tex1_ID = self.loadTexture(tex1FileName)
		tex2_ID = self.loadTexture(tex2FileName)

		tex1Location = glGetUniformLocation(self.program.program_ID, "tex1")
		glUniform1i(tex1Location, tex1_ID)

		tex2Location = glGetUniformLocation(self.program.program_ID, "tex2")
		glUniform1i(tex2Location, tex2_ID)

		glActiveTexture(GL_TEXTURE0 + tex1_ID)
		glBindTexture(GL_TEXTURE_2D, tex1_ID)

		glActiveTexture(GL_TEXTURE0 + tex2_ID)
		glBindTexture(GL_TEXTURE_2D, tex2_ID)

		glUseProgram(0)


	def loadTexture(self, texFileName):
		image = Image.open(texFileName).transpose(Image.FLIP_TOP_BOTTOM)

		texID = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texID)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE,
					 numpy.frombuffer(image.tobytes(), dtype=numpy.uint8))
		glGenerateMipmap(GL_TEXTURE_2D)
		return texID


	# Function that accepts a list of shaders, compiles them, and returns a handle to the compiled program
	@staticmethod
	def create_program(shaderList):
		programID = glCreateProgram()

		for shader in shaderList:
			glAttachShader(programID, shader)

		glLinkProgram(programID)

		status = glGetProgramiv(programID, GL_LINK_STATUS)
		if status == GL_FALSE:
			strInfoLog = glGetProgramInfoLog(programID)
			print(b"Linker failure: \n" + strInfoLog)

		# important for cleanup
		for shaderID in shaderList:
			glDetachShader(programID, shaderID)

		program = Program()
		program.program_ID = programID

		return program


class Cube(_Shape):
	def __init__(self, name, xSize, ySize, zSize, xDiv, yDiv, zDiv):
		vertices = []
		xStep = xSize / (xDiv + 1.0)
		yStep = ySize / (yDiv + 1.0)
		zStep = zSize / (zDiv + 1.0)

		#add corners
		vertices.append( Point3f(-xSize / 2.0, -ySize / 2.0, zSize / 2.0) )
		vertices.append( Point3f(xSize / 2.0, -ySize / 2.0, zSize / 2.0) )
		vertices.append( Point3f(-xSize / 2.0, ySize / 2.0, zSize / 2.0) )
		vertices.append( Point3f(xSize / 2.0, ySize / 2.0, zSize / 2.0) )
		vertices.append( Point3f(-xSize / 2.0, -ySize / 2.0, -zSize / 2.0) )
		vertices.append( Point3f(xSize / 2.0, -ySize / 2.0, -zSize / 2.0) )
		vertices.append( Point3f(-xSize / 2.0, ySize / 2.0, -zSize / 2.0) )
		vertices.append( Point3f(xSize / 2.0, ySize / 2.0, -zSize / 2.0) )

		faces = []
		faces.append( [0, 2, 3, 1] )
		faces.append( [4, 6, 7, 5] )
		faces.append( [4, 6, 2, 0] )
		faces.append( [1, 3, 7, 5] )
		faces.append( [2, 6, 7, 3] )
		faces.append( [4, 0, 1, 5] )

		_Shape.__init__(self, name, vertices, faces)
		self.drawStyle = DrawStyle.SMOOTH

		for i in range (0, len(faces) + 1):
			r = random.uniform(0, 1)
			g = random.uniform(0, 1)
			b = random.uniform(0, 1)
			self.colors.append( ColorRGBA(r, g, b, 1.0) )
