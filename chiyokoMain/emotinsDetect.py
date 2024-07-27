import argparse
from collections import Counter

import cv2
import os
import argparse

from PyQt5.QtGui import QImage, QPixmap



os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import cv2
import numpy as np
from src.model import CNN2, CNN3
from src.utils import index2emotion, cv2_img_add_text
from src.blazeface import blaze_detect


parser = argparse.ArgumentParser()
parser.add_argument("--source", type=int, default=0, help="data source, 0 for camera 1 for video")
parser.add_argument("--video_path", type=str, default=None)
opt = parser.parse_args()

if opt.source == 1 and opt.video_path is not None:
    filename = opt.video_path
else:
    filename = None

def generate_faces(face_img, img_size=48):
    """
    将探测到的人脸进行增广
    :param face_img: 灰度化的单个人脸图
    :param img_size: 目标图片大小
    :return:
    """

    face_img = face_img / 255.
    face_img = cv2.resize(face_img, (img_size, img_size), interpolation=cv2.INTER_LINEAR)
    resized_images = list()
    resized_images.append(face_img)
    resized_images.append(face_img[2:45, :])
    resized_images.append(face_img[1:47, :])
    resized_images.append(cv2.flip(face_img[:, :], 1))

    for i in range(len(resized_images)):
        resized_images[i] = cv2.resize(resized_images[i], (img_size, img_size))
        resized_images[i] = np.expand_dims(resized_images[i], axis=-1)
    resized_images = np.array(resized_images)
    return resized_images

def load_model():
    """
    加载本地模型
    :return:
    """
    model = CNN3()
    model.load_weights(r'C:\Users\Acer\Desktop\ChiyokoUI\models\cnn3_best_weights.h5')
    return model

def Camera_progress(emotions, img_queue,true_emotions,filename=0):
    model = load_model()
    capture = cv2.VideoCapture(filename)
    if filename == '':
        capture = cv2.VideoCapture(0)
    while True:
        _, frame = capture.read()
        frameForShow = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 用于在ui左下角展示
        frame = cv2.cvtColor(cv2.resize(frame, (800, 600)), cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        img_queue.put(convert_to_Qt_format)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = blaze_detect(frame)

        if faces is not None and len(faces) > 0:
            for (x, y, w, h) in faces:
                face = frame_gray[y: y + h, x: x + w]  # 脸部图片
                faces = generate_faces(face)
                results = model.predict(faces)
                result_sum = np.sum(results, axis=0).reshape(-1)
                label_index = np.argmax(result_sum, axis=0)
                emotions.append(index2emotion(label_index))
                if len(emotions) >= 100:
                    counter = Counter(emotions)
                    true_emotions.put(counter.most_common(1)[0][0])
                    emotions.clear()


        key = cv2.waitKey(30)  # 等待30ms，返回ASCII码

    # 如果输入esc则退出循环
        if key == 27:
            break


    capture.release()  # 释放摄像头
    cv2.destroyAllWindows()  # 销毁窗口