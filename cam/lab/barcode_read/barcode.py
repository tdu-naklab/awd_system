import numpy as np
import cv2
import time
import pandas as pd
from logging import getLogger, StreamHandler, DEBUG, INFO, WARN
import queue
import threading


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

    queue = queue.Queue()

    def __init__(self, *, logger=None):
        self.logger = logger or getLogger(__name__)

    def detectionStartbar(self, frame, diff_index, offset=0):
        if len(diff_index) < 15:
            logger.debug("バー検知個数不足")
            return -1, -1

        start_bar_start = 0
        for i in diff_index[diff_index >= offset]:
            # 白から黒へ
            if frame[i] == -255:
                logger.debug("開始ガイドバー 1本目 開始座標: {}".format(i))
                start_bar_start = i
                break

        if start_bar_start is 0:
            logger.debug("開始ガイドバー 1本目 未検出")
            return -1, -1

        start_bar_end = 0
        for i in diff_index[diff_index > start_bar_start]:
            # 黒から白へ
            if frame[i] == 255:
                logger.debug("開始ガイドバー 1本目 終了座標: {}".format(i))
                start_bar_end = i
                break

        if start_bar_end is 0:
            logger.debug("開始ガイドバー 1本目 終了点未検出")
            return -1, -1

        if start_bar_end - start_bar_start < 3:
            logger.debug("開始ガイドバー サイズ基準値以下")
            return -1, -1

        return start_bar_end, start_bar_start

    def detectBarcode(self, frame, diff_index, start_bar_end, min_bar_size, max_bar_size):
        # 開始ガイドバー1本目が見つかった状態から開始する
        decode_bar = [1]
        last_hit = start_bar_end
        for i in diff_index[diff_index > start_bar_end]:
            # 色が反転した箇所
            length = i - last_hit

            logger.debug("reverse: %s %s %s %s", i, length, frame[i],
                         "黒→白" if frame[i] == 255.0 else "白→黒")
            last_hit = i
            if length < min_bar_size or length < max_bar_size * 7:
                logger.debug("微小領域のノイズなのでスルー")
                return None

            for j in range(1, 7):
                if min_bar_size * j <= length <= max_bar_size * j:
                    logger.debug("範囲内: %d", j)
                    color = 1 if frame[i] == 255.0 else 0
                    for k in range(j):
                        decode_bar.append(color)
                        if len(decode_bar) == 3:
                            if not decode_bar[0:3] == [1, 0, 1]:
                                logger.debug("開始ガイドバー未検出")
                                return None
                    break

        # 最初のバーを基準に間隔を算出した結果
        logger.debug(decode_bar)
        logger.debug(len(decode_bar))
        logger.debug("開始ガイドバー: %s", decode_bar[0:3])
        if not decode_bar[0:3] == [1, 0, 1]:
            logger.debug("開始ガイドバー未検出")
            return None

        logger.debug("1桁目: %s", decode_bar[3:9])
        logger.debug("1桁目: %s", self.decodeBarcode(decode_bar[3:9], 0))

        logger.debug("2桁目: %s", decode_bar[9:15])
        logger.debug("2桁目: %s", self.decodeBarcode(decode_bar[9:15], 1))
        logger.debug("センターバー: %s", decode_bar[15:20])

        if not decode_bar[15:20] == [0, 1, 0, 1, 0]:
            logger.debug("センターバー未検出")
            return None

        logger.debug("3桁目: %s", decode_bar[20:26])
        logger.debug("3桁目: %s", self.decodeBarcode(decode_bar[20:26], 2))
        logger.debug("4桁目: %s", decode_bar[26:32])
        logger.debug("4桁目: %s", self.decodeBarcode(decode_bar[26:32], 3))
        logger.debug("終了ガイドバー: %s", decode_bar[32:35])

        if not decode_bar[32:35] == [1, 0, 1]:
            logger.debug("終了ガイドバー未検出")
            return None

        return [
            self.decodeBarcode(decode_bar[3:9], 0),
            self.decodeBarcode(decode_bar[9:15], 1),
            self.decodeBarcode(decode_bar[20:26], 2),
            self.decodeBarcode(decode_bar[26:32], 3),
        ]

    def readBarcode(self, frame, diff_index, offset=0):
        while 1:
            (start_bar_end, start_bar_start) = self.detectionStartbar(frame, diff_index, offset=offset)
            if start_bar_end is -1 or start_bar_start is -1:
                return None

            start_bar_size = start_bar_end - start_bar_start
            logger.debug("開始ガイドバー1本目 size: {}".format(start_bar_size))

            # しきい値±15%のサイズを許容する
            threshold = 0.15

            min_bar_size = start_bar_size * (1 - threshold)
            max_bar_size = start_bar_size * (1 + threshold)

            logger.debug("min_bar_size: {0:.2f}".format(min_bar_size))
            logger.debug("max_bar_size: {0:.2f}".format(max_bar_size))

            result = self.detectBarcode(frame, diff_index, start_bar_end, min_bar_size, max_bar_size)

            if result is None:
                offset = start_bar_end
            else:
                return result

    def decodeBarcode(self, code, num):
        if num is 0:
            # odd parity
            return self.odd_parity.index(code)
        else:
            # even parity
            return self.even_parity.index(code)

    def worker(self):
        while True:
            frame = self.queue.get()
            if frame is None:
                break
            try:
                result = self.readBarcode(frame)
                if result is not None:
                    logger.info("read: %s", result)
            except Exception as e:
                logger.error("cause error: %s", e)
                pass
            self.queue.task_done()


def counter(q):
    while True:
        logger.error("queue size: %s", q.qsize())
        time.sleep(1)


if __name__ == "__main__":
    logger = getLogger(__name__)
    handler = StreamHandler()

    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)

    handler.setLevel(INFO)
    logger.setLevel(INFO)

    logger.addHandler(handler)
    logger.propagate = False

    start = time.time()
    print("aa")

    frame = cv2.imread("../../ca3.png")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

    # numpyを使って転地して横方向に反転
    frame = frame.transpose()[:, ::-1]

    reader = BarcodeReader(logger=logger)

    f = pd.DataFrame(frame)
    f = f.astype("int64")
    frame_d = f.diff()

    for index in range(len(frame_d.columns)):
        logger.debug("%s本目", index)
        diff_index = frame_d[index].index[frame_d[index].isin([-255, 255])]
        result = reader.readBarcode(frame_d[index], diff_index)
        if result is not None:
            logger.info("read: %s", result)

    duration = time.time() - start
    logger.info("time: {0:.4f}".format(duration * 1000) + "[ms] {0:.2f}".format(1 / duration) + "[fps]")

    # cv2.imshow("aa", frame_d.values)
    # cv2.imshow("ab", frame.values)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
