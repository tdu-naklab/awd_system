import numpy as np
import cv2
import time
import pandas as pd


class BarcodeReader:
    odd_parity = [
        [0, 1, 1, 0, 0, 1],
        [0, 0, 1, 1, 0, 1],
        [0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 1, 1],
        [0, 0, 1, 0, 1, 1],
    ]

    even_parity = [
        [1, 0, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [1, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 0],
    ]

    guide_bar = [1, 0, 1]
    center_bar = [0, 1, 0, 1, 0]

    def readBarcode(self, frame, offset=0):
        frameSize = len(frame[0])

        startBarStart = 0
        for i in range(offset, frameSize):
            # 白から黒へ
            if frame[0][i] == -255:
                print("start bar 1本目 開始座標:", i)
                startBarStart = i
                break

        startBarEnd = 0
        for i in range(startBarStart, frameSize):
            # 黒から白へ
            if frame[0][i] == 255:
                print("start bar 1本目 終了座標:", i)
                startBarEnd = i
                break

        startBarSize = startBarEnd - startBarStart
        print("startbar size:", startBarSize)

        # しきい値±10%のサイズを許容する
        threshold = 0.15

        minBarSize = startBarSize * (1 - threshold)
        maxBarSize = startBarSize * (1 + threshold)

        print("minBarSize: {0:.2f}".format(minBarSize))
        print("maxBarSize: {0:.2f}".format(maxBarSize))

        decodeBar = [1]
        lastHit = startBarEnd
        for i in range(startBarEnd + 1, frameSize):
            # 色が反転した箇所
            if frame_d[0][i] != 0:
                length = i - lastHit

                color = "黒→白" if frame_d[0][i] == 255.0 else "白→黒"
                print("reverse: ", i, length, frame_d[0][i], color)
                lastHit = i
                for j in range(1, 7):
                    if minBarSize * j <= length <= maxBarSize * j:
                        print("範囲内:", j)
                        color = 1 if frame_d[0][i] == 255.0 else 0
                        for k in range(j): decodeBar.append(color)
                        break

        # 最初のバーを基準に間隔を算出した結果
        try:
            print(decodeBar)
            print("開始ガイドバー:", decodeBar[0:3])
            if not decodeBar[0:3] == [1, 0, 1]:
                raise Exception("開始ガイドバー未検出")

            print("1桁目:", decodeBar[3:9])
            print("2桁目:", decodeBar[9:15])
            print("センターバー:", decodeBar[15:20])

            if not decodeBar[15:20] == [0, 1, 0, 1, 0]:
                raise Exception("センターバー未検出")

            print("3桁目:", decodeBar[20:26])
            print("4桁目:", decodeBar[26:32])
            print("終了ガイドバー:", decodeBar[32:35])

            if not decodeBar[32:35] == [1, 0, 1]:
                raise Exception("終了ガイドバー未検出")
        except Exception as e:
            print("cause error:", e.message)
            self.readBarcode(frame, startBarEnd)


if __name__ == "__main__":
    start = time.time()
    print("aa")

    frame = cv2.imread("./tr.png")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
    frame = pd.DataFrame(frame[0])
    frame = frame.astype("int64")
    frame_d = frame.diff()

    reader = BarcodeReader()
    reader.readBarcode(frame_d)

    duration = time.time() - start
    print("time: {0:.4f}".format(duration * 1000) + "[ms] {0:.2f}".format(1 / duration) + "[fps]")

    # cv2.imshow("aa", frame_d.values)
    # cv2.imshow("ab", frame.values)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
