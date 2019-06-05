import numpy as np
import cv2
import time
import pandas as pd

odd_parity = np.array([
    [0, 1, 1, 0, 0, 1],
    [0, 0, 1, 1, 0, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 1, 0, 0, 1, 1],
    [0, 0, 1, 0, 1, 1],
])

even_parity = np.array([
    [1, 0, 0, 1, 1, 0],
    [1, 0, 1, 1, 0, 0],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 1, 0],
    [1, 1, 0, 1, 0, 0],
])

guide_bar = np.array([1, 0, 1])
center_bar = np.array([0, 1, 0, 1, 0])

if __name__ == "__main__":
    start = time.time()
    print("aa")

    frame = cv2.imread("./tr2.png")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
    frame = pd.DataFrame(frame[0])
    frame = frame.astype("int64")
    frame_d = frame.diff()

    startBar = 0
    for i in range(len(frame_d[0])):
        # 白から黒へ
        if frame_d[0][i] == -255:
            print("start bar start:", i)
            startBar = i
            break

    startBarEnd = 0
    for i in range(startBar, len(frame_d[0]) - startBar):
        # 黒から白へ
        if frame_d[0][i] == 255:
            print("start bar end:", i)
            startBarEnd = i
            break
    print("startBarEnd:", startBarEnd)

    a = pd.concat([frame, frame_d], axis=1)
    print(a)

    duration = time.time() - start
    print("time: {0:.4f}".format(duration * 1000) + "[ms] {0:.2f}".format(1 / duration) + "[fps]")

    # cv2.imshow("aa", frame_d.values)
    # cv2.imshow("ab", frame.values)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
