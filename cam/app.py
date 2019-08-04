import numpy as np
import cv2
from PIL import Image
from enum import Enum
import time
import urllib.request
import json
import zbarlight

WIDTH = 1920
HEIGHT = 1080
FPS = 60
SEARCH_LINE = [250, 550, 850]
SERVER_URL = 'http://localhost:3000'
HTTP_HEADERS = {'Content-Type": "application/json'}


class State(Enum):
    WAITING = 0
    REGISTERING = 1
    RACING = 2
    FINISHED = 3


def main():
    state = State.WAITING

    # cap = cv2.VideoCapture('./miniyonku4.mp4')
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FPS, FPS)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    players = [None, None, None]
    detected_players_array = [[], [], []]
    players_start_time = [None, None, None]
    players_time = [None, None, None]
    players_mask = [False, False, False]

    while True:
        ret, frame = cap.read()
        screen = frame.copy()
        key = cv2.waitKey(20) & 0xFF

        # 常に表示する項目
        result = [None, None, None]
        for i in range(3):
            # 走査範囲を表す線を描画
            result[i] = read_barcode(frame, SEARCH_LINE[i])
            screen = cv2.line(screen, (0, SEARCH_LINE[i] - 150), (WIDTH, SEARCH_LINE[i] - 150), (0, 255, 0), 1)
            screen = cv2.line(screen, (0, SEARCH_LINE[i]), (WIDTH, SEARCH_LINE[i]), (0, 0, 255), 1)
            screen = cv2.line(screen, (0, SEARCH_LINE[i] + 150), (WIDTH, SEARCH_LINE[i] + 150), (0, 255, 0), 1)
            # プレイヤーのバーコードを表示
            cv2.putText(screen, str(players[i]), (int(WIDTH/4*1), SEARCH_LINE[i]), cv2.FONT_HERSHEY_PLAIN, 2, (33, 33, 33), 2, cv2.LINE_AA)
            # 検出したバーコードを表示
            cv2.putText(screen, str(result[i]), (int(WIDTH/4*2), SEARCH_LINE[i]), cv2.FONT_HERSHEY_PLAIN, 2, (33, 33, 33), 2, cv2.LINE_AA)
            # タイムを表示
            if players_time[i] is None:
                cv2.putText(screen, str(players_time[i]), (int(WIDTH/4*3), SEARCH_LINE[i]), cv2.FONT_HERSHEY_PLAIN, 2, (33, 33, 33), 2, cv2.LINE_AA)
            else:
                cv2.putText(screen, str(players_time[i]), (int(WIDTH/4*3), SEARCH_LINE[i]), cv2.FONT_HERSHEY_PLAIN, 2, (54, 67, 244), 2, cv2.LINE_AA)

        # ここからstate別処理
        # WAITING
        if state == State.WAITING:
            cv2.putText(screen, 'Waiting', (0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (80, 175, 76), 4, cv2.LINE_AA)
            # 変数初期化
            players = [None, None, None]
            detected_players_array = [[], [], []]
            players_start_time = [None, None, None]
            players_time = [None, None, None]
            players_mask = [False, False, False]

        # REGISTERING
        elif state == State.REGISTERING:
            cv2.putText(screen, 'Registering', (0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (0, 152, 255), 4, cv2.LINE_AA)
            # バーコードを検出
            if any(result):
                # 登録用APIを叩く処理
                print(result)

        # RACING
        elif state == State.RACING:
            cv2.putText(screen, 'Running', (0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (54, 67, 244), 4, cv2.LINE_AA)

            for i in range(3):
                # 検出時
                if result[i] is not None:
                    # 初回
                    if len(detected_players_array[i]) == 0:
                        print('started: ' + result[i])
                        players[i] = result[i]
                        detected_players_array[i].append(result[i])
                        players_start_time[i] = time.time()
                    # 2回目以降
                    elif time.time() - players_start_time[i] > 1:
                        print('detected: ' + result[i])
                        detected_players_array[i].append(result[i])
                        # ゴール時
                        if detected_players_array[i][0] == detected_players_array[i][-1] and players_time[i] is None:
                            print('goal: ' + result[i])
                            players_time[i] = round(time.time() - players_start_time[i], 3)
                            print(players_time[i])

        # FINISHED
        elif state == State.FINISHED:
            cv2.putText(screen, 'Processing', (0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (243, 150, 33), 4, cv2.LINE_AA)
            for i in range(3):
                cv2.putText(screen, (str(players_time[i]) + ': OK?'), (int(WIDTH / 4 * 3), SEARCH_LINE[i]), cv2.FONT_HERSHEY_PLAIN, 2, (54, 67, 244), 4, cv2.LINE_AA)

        # 描画
        cv2.imshow('screen', screen)

        # キー操作
        if key == 27:  # Escape プログラム終了
            break

        elif key == ord(' '):  # Space 次へ進む
            if state == State.WAITING:
                state = State.REGISTERING
            elif state == State.REGISTERING:
                state = State.RACING
            elif state == State.RACING:
                state = State.FINISHED

        elif state == State.RACING and key == ord('q'):  # Q 試合やりなおし
            players = [None, None, None]
            detected_players_array = [[], [], []]
            players_start_time = [None, None, None]
            players_time = [None, None, None]

    cap.release()
    cv2.destroyAllWindows()


def shear(image, deg):
    h, w = image.shape[:2]
    src = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]], np.float32)
    dest = src.copy()
    dest[:, 0] += (deg / h * (h - src[:, 1])).astype(np.float32)
    affine = cv2.getAffineTransform(src, dest)
    return cv2.warpAffine(image, affine, (w, h))


def read_barcode(frame, y):
    search_line = (frame[y, :, 0] < 100) * (frame[y, :, 1] < 100) * (frame[y, :, 2] > 200)
    detected_pos = 0
    for i in reversed(range(200, WIDTH)):
        if search_line[i]:
            detected_pos = i
            break
    if detected_pos != 0:
        barcode = frame[y - 150:y + 150, detected_pos - 100:detected_pos]
        for deg in range(20, 60, 5):
            sheared = shear(barcode, deg)
            sheared_pil = Image.fromarray(cv2.cvtColor(sheared, cv2.COLOR_BGR2RGB))
            detected_barcode = zbarlight.scan_codes('upce', sheared_pil)

            if detected_barcode is not None:
                result = detected_barcode[0].decode('utf-8')[1:7]
                return result

    return None


if __name__ == "__main__":
    main()
