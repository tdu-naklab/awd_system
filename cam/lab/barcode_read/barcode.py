import numpy as np
import cv2
import time
import pandas as pd
from logging import getLogger, StreamHandler, DEBUG, INFO, WARN


class BarcodeReader:
    logger = None

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

    def __init__(self, *, logger=None):
        self.logger = logger or getLogger(__name__)

    def readBarcode(self, frame, offset=0):
        frameSize = len(frame)

        while 1:
            if frameSize < offset + 32:
                # 検出する最低桁数が32桁以上なので、ここで一列分の検出は終了する
                raise Exception("1列終了")

            startBarStart = 0
            for i in range(offset, frameSize):
                # 白から黒へ
                if frame[0][i] == -255:
                    logger.debug("開始ガイドバー 1本目 開始座標: {}".format(i))
                    startBarStart = i
                    break

            if startBarStart is 0:
                raise Exception("開始ガイドバー 1本目 未検出")

            startBarEnd = 0
            for i in range(startBarStart, frameSize):
                # 黒から白へ
                if frame[0][i] == 255:
                    logger.debug("開始ガイドバー 1本目 終了座標: {}".format(i))
                    startBarEnd = i
                    break

            if startBarEnd is 0:
                raise Exception("開始ガイドバー 1本目 終了点未検出")

            startBarSize = startBarEnd - startBarStart
            logger.debug("開始ガイドバー1本目 size: {}".format(startBarSize))

            # しきい値±10%のサイズを許容する
            threshold = 0.15

            minBarSize = startBarSize * (1 - threshold)
            maxBarSize = startBarSize * (1 + threshold)

            logger.debug("minBarSize: {0:.2f}".format(minBarSize))
            logger.debug("maxBarSize: {0:.2f}".format(maxBarSize))

            try:
                decodeBar = [1]
                lastHit = startBarEnd
                for i in range(startBarEnd + 1, frameSize):
                    # 色が反転した箇所
                    if frame_d[0][i] != 0:
                        length = i - lastHit

                        logger.debug("reverse: %s %s %s %s", i, length, frame_d[0][i],
                                     "黒→白" if frame_d[0][i] == 255.0 else "白→黒")
                        lastHit = i
                        for j in range(1, 7):
                            if minBarSize * j <= length <= maxBarSize * j:
                                logger.debug("範囲内: %d", j)
                                color = 1 if frame_d[0][i] == 255.0 else 0
                                for k in range(j):
                                    decodeBar.append(color)
                                    if len(decodeBar) == 3:
                                        if not decodeBar[0:3] == [1, 0, 1]:
                                            raise Exception("開始ガイドバー未検出")
                                break

                # 最初のバーを基準に間隔を算出した結果
                logger.debug(decodeBar)
                logger.debug(len(decodeBar))
                logger.debug("開始ガイドバー: %s", decodeBar[0:3])
                if not decodeBar[0:3] == [1, 0, 1]:
                    raise Exception("開始ガイドバー未検出")

                logger.debug("1桁目: %s", decodeBar[3:9])
                logger.debug("1桁目: %s", self.decodeBarcode(decodeBar[3:9], 0))

                logger.debug("2桁目: %s", decodeBar[9:15])
                logger.debug("2桁目: %s", self.decodeBarcode(decodeBar[9:15], 1))
                logger.debug("センターバー: %s", decodeBar[15:20])

                if not decodeBar[15:20] == [0, 1, 0, 1, 0]:
                    raise Exception("センターバー未検出")

                logger.debug("3桁目: %s", decodeBar[20:26])
                logger.debug("3桁目: %s", self.decodeBarcode(decodeBar[20:26], 2))
                logger.debug("4桁目: %s", decodeBar[26:32])
                logger.debug("4桁目: %s", self.decodeBarcode(decodeBar[26:32], 3))
                logger.debug("終了ガイドバー: %s", decodeBar[32:35])

                if not decodeBar[32:35] == [1, 0, 1]:
                    raise Exception("終了ガイドバー未検出")

                return [
                    self.decodeBarcode(decodeBar[3:9], 0),
                    self.decodeBarcode(decodeBar[9:15], 1),
                    self.decodeBarcode(decodeBar[20:26], 2),
                    self.decodeBarcode(decodeBar[26:32], 3),
                ]
            except Exception as e:
                # logger.error("cause error: %s", e)
                offset = startBarEnd
                pass


def decodeBarcode(self, code, num):
    if num is 0 or num is 3:
        # odd parity
        return self.odd_parity.index(code)
    else:
        # even parity
        return self.even_parity.index(code)


if __name__ == "__main__":
    logger = getLogger(__name__)
    handler = StreamHandler()

    handler.setLevel(INFO)
    logger.setLevel(INFO)

    # handler.setLevel(DEBUG)
    # logger.setLevel(DEBUG)

    logger.addHandler(handler)
    logger.propagate = False

    start = time.time()
    print("aa")

    frame = cv2.imread("./tr.png")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

    reader = BarcodeReader(logger=logger)

    for index in range(len(frame)):
        f = pd.DataFrame(frame[index])
        f = f.astype("int64")
        frame_d = f.diff()
        try:
            readResult = reader.readBarcode(frame_d)
            logger.debug("read result: %s", readResult)
        except Exception as e:
            logger.error("cause error main: %s %s", index, e)
            pass

    duration = time.time() - start
    logger.info("time: {0:.4f}".format(duration * 1000) + "[ms] {0:.2f}".format(1 / duration) + "[fps]")

    # cv2.imshow("aa", frame_d.values)
    # cv2.imshow("ab", frame.values)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
