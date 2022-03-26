
from camera import *
from view import *
from fileIO import FileIO
from shapes import *


def main():
    # global view
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowSize(640, 640)
    glutInitWindowPosition(200, 200)

    window = glutCreateWindow("CENG487 Assignment")

    # create camera
    camera = Camera()
    camera.createView(Point3f(0.0, 0.0, 10.0),
					  Point3f(0.0, 0.0, 0.0),
					  Vector3f(0.0, 1.0, 0.0))
    camera.setNear(1)
    camera.setFar(1000)

    # create View
    view = View(camera)

    # init scene
    scene = Scene()
    view.setScene(scene)

    shape_tuple = FileIO.read_file(sys.argv[1])
    cube = _Shape(shape_tuple[0], shape_tuple[1], shape_tuple[2], shape_tuple[3], shape_tuple[4])
    scene.add(cube)

    # define callbacks
    glutDisplayFunc(view.draw)
    glutIdleFunc(view.idleFunction)
    glutKeyboardFunc(view.keyPressed)
    glutSpecialFunc(view.specialKeyPressed)
    glutMouseFunc(view.mousePressed)
    glutMotionFunc(view.mouseMove)

    # Start Event Processing Engine
    glutMainLoop()


# Print message to console, and kick off the main to get it rolling.
main()
