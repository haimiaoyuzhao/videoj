from PyQt5.QtWidgets import QMainWindow
from time import sleep
import sys

from video_window import Ui_VideoWindow
from imgbox import decorate_qwidget_with_imgbox
from my_qwidget import decorate_qwidget_with_input_dev
from player import Player


VIDEO_PALYING = 0
VIDEO_PAUSING = 1


class MyVideoWindow(Ui_VideoWindow):
    def __init__(self, window: QMainWindow, video_path: str):
        super().__init__()
        self.window = window
        self.window.closeEvent = self.closeEvent
        self.setupUi(self.window)
        self.centralwidget = decorate_qwidget_with_input_dev(self.centralwidget, self)
        self.widget = decorate_qwidget_with_imgbox(self.widget)
        print(video_path)

        self.video_player = Player(self.window, video_path, self)
        self.state = VIDEO_PALYING  # 设置当前播放器处于的状态，播放还是暂停
        self.tot_secs = self.video_player.get_tot_secs()
        self.cur_sec = 0
        self._init_win_info()

        # 设置速率
        self.speed_cbox.currentIndexChanged.connect(self._speed_changed)
        self.horizontalScrollBar.valueChanged.connect(self._jump)

    def closeEvent(self, event):
        self._quit()

    def start_play(self):
        sleep(1)
        self.play()

    def fast_forward(self):
        # 前进10s
        new_sec = self.cur_sec + 10
        self.horizontalScrollBar.setValue(new_sec)

    def back_forward(self):
        # 后退10s
        new_sec = self.cur_sec - 10
        self.horizontalScrollBar.setValue(new_sec)

    def play(self):
        self.state = VIDEO_PALYING
        self.video_player.play()

    def pause(self):
        self.state = VIDEO_PAUSING
        self.video_player.pause()

    def change_state(self):
        if self.state == VIDEO_PALYING:
            self.state = VIDEO_PAUSING
            self.pause()
        elif self.state == VIDEO_PAUSING:
            self.state = VIDEO_PALYING
            self.play()

    def display(self, cur_sec, frame):
        self.widget.draw(frame)
        self.cur_sec = cur_sec
        self._update_win_info()

    def _quit(self):
        print("close")
        self.video_player.quit()
        self.window.close()

    def _init_win_info(self):
        """
        初始化窗口中的部分信息
        :return:
        """
        self.time_label.setText(self._cal_time_label())
        self.horizontalScrollBar.setRange(0, self.tot_secs)
        self.horizontalScrollBar.setValue(0)

    def _update_win_info(self):
        """
        更新窗口中的部分信息
        :return:
        """
        self.time_label.setText(self._cal_time_label())
        self.horizontalScrollBar.setValue(self.cur_sec)

    def _cal_time_label(self) -> str:
        return f"{str.zfill(str(self.cur_sec//60), 2)}:{str.zfill(str(self.cur_sec%60), 2)}/" \
               f"{str.zfill(str(self.tot_secs//60), 2)}:{str.zfill(str(self.tot_secs%60), 2)}"

    def _speed_changed(self):
        text = self.speed_cbox.currentText()
        times = 1
        if text == '1x':
            times = 1
        elif text == '0.5x':
            times = 0.5
        elif text == '2x':
            times = 2
        elif text == '3x':
            times = 3
        self.video_player.mult_speed_by(times)
        cur_state = self.state  # 记录当前状态，如果在jump前就是暂停状态，那么就不用play了
        if cur_state != VIDEO_PALYING:
            self.play()

    def _jump(self):
        """
        当改变进度条时读取新的数据
        :return:
        """
        if self.horizontalScrollBar.value() >= self.horizontalScrollBar.maximum():
            self._quit()
        if abs(self.cur_sec - self.horizontalScrollBar.value()) <= 2:
            # 代表时滑动条自己滑过去的，不存在跳跃情况
            return
        value = self.horizontalScrollBar.value()
        print(__file__, sys._getframe().f_lineno, " jump to: ", value)
        cur_state = self.state  # 记录当前状态，如果在jump前就是暂停状态，那么就不用play了
        self.pause()
        self.video_player.jump_to(value)
        if cur_state == VIDEO_PALYING:
            self.play()
        print(__file__, sys._getframe().f_lineno, "jump success")

