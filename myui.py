from PyQt5.QtWidgets import QMainWindow

from main_window import Ui_MainWindow
from myvideo_win import MyVideoWindow
from my_qwidget import decorate_qwidget_with_drag



class MyUiWindow(Ui_MainWindow):
    def __init__(self, window: QMainWindow, args):
        super().__init__()
        self.window = window
        self.setupUi(self.window)
        self.centralwidget = decorate_qwidget_with_drag(self.centralwidget, self)
        self.video_wins = []
        if len(args) > 1:
            self.start_play(args[1])

    def start_play(self, path):
        if not path.endswith("mp4") and not path.endswith("avi"):
            print(path, " is not valid")
            return
        v_window = QMainWindow()
        video_win = MyVideoWindow(v_window, path)
        video_win.start_play()
        v_window.show()
        self.video_wins.append(video_win)