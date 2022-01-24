from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtCore import Qt
from utils import check_system
import sys


def decorate_qwidget_with_drag(qwidget: QWidget, main_ui):
    QWidgetWithDrag(qwidget, main_ui)
    return qwidget

def decorate_qwidget_with_input_dev(qwidget: QWidget, main_ui):
    QWidgetWithInputDev(qwidget, main_ui)
    return qwidget


class QWidgetWithDrag():
    def __init__(self, qwidget: QWidget, main_ui):
        qwidget.setAcceptDrops(True)
        qwidget.dragEnterEvent = self.dragEnterEvent
        qwidget.dropEvent = self.dropEvent
        self.qwidget = qwidget
        self.main_ui = main_ui

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e) -> None:
        file_path = e.mimeData().text()
        if check_system() == "windows":
            file_path = file_path[8:]
        else:
            file_path = file_path[7:]
        self.main_ui.start_play(file_path)


class QWidgetWithInputDev:
    def __init__(self, qwidget: QWidget, main_ui):
        qwidget.setAcceptDrops(True)
        qwidget.setFocus()  # 不加这句话无法监听键盘
        qwidget.keyPressEvent = self.keyPressEvent
        qwidget.mousePressEvent = self.mousePressEvent
        self.qwidget = qwidget
        self.main_ui = main_ui
        self.isLeftPressed = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.main_ui.fast_forward()
        elif event.key() == Qt.Key_Left:
            self.main_ui.back_forward()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 左键按下
            print("鼠标左键单击")  # 响应测试语句
            if self.isLeftPressed:
                self.isLeftPressed = False
            else:
                self.isLeftPressed = True  # 左键按下(图片被点住),置Ture
                self.main_ui.change_state()
