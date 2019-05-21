from OpenGL.GL import *
from OpenGL.GLUT import *
import cv2
import time


class SpeedAnalysis:
    def __init__(self, capture, width, height, draw):
        print("start")
        self.width = width
        self.height = height
        self.capture = capture

        glutInitWindowPosition(0, 0)
        glutInitWindowSize(width, height)
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        self.window = glutCreateWindow("SpeedAnalysis")
        glutDisplayFunc(draw)
        glutReshapeFunc(self.reshape)
        self.init()
        glutIdleFunc(self.idle)
        glutKeyboardFunc(self.keyboard)

    def draw(self, frame):
        print(format("loop start, num: {}".format(self.window), "*^32"))

        glutSetWindow(self.window)
        start = time.time()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, -1)

        # ここに処理を書く

        # imshowも使えますが、遅延がひどいので今回はOpenGLを使います。
        # cv2.imshow("a", frame)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(1.0, 1.0, 1.0)
        glDrawPixels(frame.shape[1], frame.shape[0], GL_RGB, GL_UNSIGNED_BYTE, frame)
        glFlush()
        glutSwapBuffers()
        print("showing time:{0:.2f}".format(1 / (time.time() - start)) + "[fps]")

    def init(self):
        print("init open GL with ")
        glClearColor(0.7, 0.7, 0.7, 0.7)

    def idle(self):
        print("idle")
        glutPostRedisplay()

    def reshape(self, w, h):
        print("reshape")
        glViewport(0, 0, w, h)
        glLoadIdentity()
        # Make the display area proportional to the size of the view
        glOrtho(-w / self.width, w / self.width, -h / self.height, h / self.height, -1.0, 1.0)

    def keyboard(self, key, x, y):
        # convert byte to str
        key = key.decode('utf-8')
        # press q to exit
        if key == 'q':
            print('exit')
            cv2.destroyAllWindows()
            sys.exit()
