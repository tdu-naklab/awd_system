import time

from SpeedAnalysis import *
from RapTime import *
from OpenGL.GL import *
from OpenGL.GLUT import *

import cv2

# CONFIGURATION
WIDTH = 800
HEIGHT = 448
FPS = 30

###########################################

print(format("start camera system", "*^32"))
cap = cv2.VideoCapture(0)
print("camera default config, width:  {0}".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("camera default config, height: {0}".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("camera default config, fps:    {0}".format(cap.get(cv2.CAP_PROP_FPS)))

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

print("camera set to config, width:  {0}".format(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("camera set to config, height: {0}".format(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("camera set to config, fps:    {0}".format(cap.get(cv2.CAP_PROP_FPS)))
print("camera set to config, fps:    {0}".format(cap.get(cv2.CAP_PROP_FOURCC)))

print(format("capture start", "*^32"))


def draw():
    ret, frame = cap.read()
    if frame is None:
        return

    speedAnalysis.draw(frame)
    raptime.draw(frame)


speedAnalysis = SpeedAnalysis(cap, WIDTH, HEIGHT, draw)
raptime = RapTime(cap, WIDTH, HEIGHT, draw)


def main():
    # glutDisplayFunc()
    glutMainLoop()


if __name__ == "__main__":
    main()
