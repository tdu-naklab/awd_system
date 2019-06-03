# awd_system
設計製作のやつ

## うごかしかた(without RasPi)

### Required
Python >= 3.7.3
別途OpenGL必要かも　※要参照

### Install
```
$ cd cam
$ pip install -r requirements.txt
```

### Running
```
$ cd cam
$ python app.py
```


## Raspberry Pi3向けセットアップ
thanks for https://qiita.com/mt08/items/e8e8e728cf106ac83218

### Python3を入れる
`pyenv`などで入れても良いのですが、numpyなどをソースからビルドする必要があったり、後述するOpenCVのインストールとの兼ね合いもあるので、aptを使って入れます。

```
$ sudo apt install -y build-essential cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libcanberra-gtk* libatlas-base-dev gfortran python3-dev python3-numpy python3-opengl
```

### OpenCVのインストール

```
OPENCV_DEB=libopencv4_4.1.0-20190415.1_armhf.deb
curl -SL https://github.com/mt08xx/files/raw/master/opencv-rpi/${OPENCV_DEB} -o ${OPENCV_DEB}
sudo apt autoremove -y libopencv{3,4}
sudo apt install -y ./${OPENCV_DEB}

#
sudo ldconfig
python2 -c 'import cv2; print(cv2.__version__)'
python3 -c 'import cv2; print(cv2.__version__)'
```
