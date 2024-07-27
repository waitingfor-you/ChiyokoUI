import datetime
import os
import sys
import queue

from collections import deque
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QLabel, QDesktopWidget
from PyQt5 import QtGui

from chiyokoMain.CameraSet import CameraSet
from chiyokoMain.TimerThread import TimerThread
from emotinsDetect import *

filename = ''   # 用于调用摄像头，0为本地摄像头，但是无法直接输入192.168.1.100这样子的，需要加工
emotions = []   # 用于储存认为的表情
img_queue = queue.Queue() # 用于储存摄像头传来的图像,这东西是不怕炸的，会自动
true_emotions = queue.Queue() # 用于储存摄像头传来的图像,这东西是不怕炸的，会自动
emodict = {'发怒': 'anger',
        '厌恶': 'disgust',
        '恐惧': 'fear',
        '开心': 'happy',
        '伤心': 'sad',
        '惊讶': 'surprised',
        '中性': 'neutral',
        '蔑视': 'contempt'
           }

path = r'C:\Users\Acer\Desktop\ChiyokoUI\assets\icons'

class Chiyoko(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ChiyokoUI")
        self.setFixedSize(1618, 910)

        self.center_window()  # 居中窗口的方法
        self.set_background(r"C:\Users\Acer\Desktop\ChiyokoUI\chiyokobg\zero.png")
        CameraSet(filename, emotions, img_queue, true_emotions)
        self.create_widget()

        self.timerthread = TimerThread()
        self.timerthread.start()
        self.timerthread.signal.connect(self.update_time)


    def center_window(self):
        # 获取屏幕的可用几何信息
        screen_geometry = QDesktopWidget().availableGeometry()
        # 获取窗口自身的几何信息
        window_geometry = self.frameGeometry()
        # 将窗口移动到屏幕中央
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def create_widget(self):
        # 顶部区域
        self.top_frame = QLabel()
        self.top_frame.setFixedSize(1500, 500)
        self.top_frame.setStyleSheet('QLabel { border: 2px solid gray; }')
        self.top_frame.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)



        # 左下角 上面为摄像头，下面为时间
        self.camera_frame = QWidget()
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(200, 170)

        self.camera_label.setStyleSheet('QLabel { border: 2px solid gray; }')

        self.timer_frame = QWidget()
        self.timer_label = QLabel()
        self.timer_label.setFixedSize(200, 190)
        font = QtGui.QFont()
        font.setBold(True)
        font.setFamily("华文楷体")
        font.setPointSize(14)
        self.timer_label.setFont(font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet('QWidget { border: 2px solid gray; }')

        leftbottom_layout = QVBoxLayout()
        leftbottom_layout.addWidget(self.camera_label)
        leftbottom_layout.addWidget(self.timer_label)

        # 右下角 对话框
        self.dialog_frame = QWidget()
        self.dialog_frame.setFixedSize(1200, 360)
        self.dialog_frame.setStyleSheet('QWidget { border: 2px solid gray; }')

        # 底部整体布局
        self.bottom_frame = QWidget()
        self.bottom_frame.setFixedSize(1450, 380)
        self.bottom_frame.setStyleSheet('QWidget { border: 2px solid gray; }')

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(leftbottom_layout)
        bottom_layout.addWidget(self.dialog_frame)

        self.bottom_frame.setLayout(bottom_layout)

        # 主界面
        main_layout = QVBoxLayout()

        # 创建一个水平布局，将顶部区域居中显示
        center_top_layout = QHBoxLayout()
        center_top_layout.addStretch(1)  # 添加一个弹簧以将顶部区域推到中间
        center_top_layout.addWidget(self.top_frame)
        center_top_layout.addStretch(1)  # 再次添加一个弹簧以保持顶部区域居中

        main_layout.addLayout(center_top_layout)
        main_layout.addWidget(self.bottom_frame)

        self.setLayout(main_layout)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.image_show)
        self.timer2.start(18)

        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.image_update)
        self.timer3.start(18)

    def set_background(self, path):
        if path:
            pixmap = QPixmap(path)
            if pixmap.size() != (1618,910):
               pixmap = pixmap.scaled(1618,910, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.Background, QBrush(pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet('background: lightgray')

    def update_time(self, text):
        now = datetime.datetime.now()
        self.timer_label.setText(f'{text}')

    def image_show(self):
        if not img_queue.empty():
            frame = img_queue.get_nowait()  # 从队列中获取 QImgae 对象
            label_width = self.camera_label.width()  # 获取 label 的宽度
            label_height = self.camera_label.height()  # 获取 label 的高度

            # 调整图像尺寸
            scaled_img = frame.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 将 QImage 转换为 QPixmap 以便在 QLabel 中显示
            pixmap = QPixmap.fromImage(scaled_img)

            # 设置 QLabel 的 pixmap
            self.camera_label.setPixmap(pixmap)
    def image_update(self):
        if not true_emotions.empty():
            true_emotion = true_emotions.get_nowait()
            true_emotion = emodict[true_emotion]
            emopath = os.path.join(path, '{}.png'.format(true_emotion))
            pixmap = QPixmap(emopath)
            pixmap.scaled(600, 400)
            if pixmap.isNull():
                print(f"Failed to load image from {emopath}")
            self.top_frame.setPixmap(pixmap)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chiyoko = Chiyoko()
    chiyoko.show()
    sys.exit(app.exec_())
