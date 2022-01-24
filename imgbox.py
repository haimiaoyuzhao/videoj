import cv2
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QPoint
import numpy as np


def decorate_qwidget_with_imgbox(qwidget: QWidget):
    """
    将部件装饰成一个能够展示图像的画布
    """
    return ImageBox(qwidget)


class ImageBox:
    def __init__(self, qwidget: QWidget, father=None):
        self.qwidget = qwidget
        father = None
        qwidget.setMouseTracking(True)
        qwidget.add_father = self.add_father
        self.father = father

        qwidget.paintEvent = self.paintEvent

        self.img = None
        self.singleOffset = QPoint(0, 0)  # 初始化偏移值

    def draw(self, img):
        self.img = img
        self.qwidget.repaint()

    def add_father(self, father):
        self.father = father

    def paintEvent(self, event):
        # print("repaint")
        bg = np.zeros(shape=(self.qwidget.width(), self.qwidget.height()), dtype=np.uint8)
        bg = QImage(bg, bg.shape[0], bg.shape[1], bg.shape[0], QImage.Format_Grayscale8)
        bg = QPixmap.fromImage(bg)

        self.imgPainter = QPainter()  # 用于动态绘制图片
        self.imgPainter.begin(self.qwidget)  # 无begin和end,则将一直循环更新
        # 画背景
        self.imgPainter.drawPixmap(QPoint(0, 0), bg)
        # 画图像
        if self.img is not None:
            img = self.img
            img = cv2.resize(img, (self.qwidget.width(), self.qwidget.height()))
            if img.ndim == 2:
                height, width = img.shape
                bytesPerComponent = 1
            else:
                height, width, bytesPerComponent = img.shape
            bytesPerLine = bytesPerComponent * width
            img_shape = img.shape
            if bytesPerComponent == 1:
                format = QImage.Format_Grayscale8
            elif bytesPerComponent == 3:
                format = QImage.Format_RGB888
            elif bytesPerComponent == 4:
                format = QImage.Format_ARGB32
            else:
                print("format is error")
                return
            img = QImage(img, width, height, bytesPerLine, format)
            img = QPixmap.fromImage(img)
            self.imgPainter.drawPixmap(self.singleOffset, img)  # 从图像文件提取Pixmap并显示在指定位置

        self.imgPainter.end()  # 无begin和end,则将一直循环更新



