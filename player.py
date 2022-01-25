from PyQt5.QtCore import QTimer
from time import time

from pyaudio import PyAudio

from reader import VideoReader, AudioReader


class Player:
    def __init__(self, window, video_path, father):
        self.father = father
        self.window = window
        self.video_reader = VideoReader(video_path)

        self.audio_reader = AudioReader(video_path, self.video_reader.tot_frame)
        p = PyAudio()  # 初始化PyAudio模块
        self.stream = p.open(format=p.get_format_from_width(self.audio_reader.nbytes),
                             channels=self.audio_reader.nchannels,
                             rate=self.audio_reader.fps, output=True)

        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self._play_frame)  # 到达设定的时间后，执行槽函数代码

        self.ini_fps = int(self.video_reader.get_fps())  # 视频自带的fps值
        self.fps = self.ini_fps  # 当前视频读取软件设置的fps值，因为有加速，所以跟上一个并不总是相等
        self.cur_frame_id = 0
        self.cur_time = None

        self.tot_frame = int(self.video_reader.get_tot_frame())
        self.tot_secs = self.tot_frame // self.ini_fps

    def _play_frame(self):
        cur_time = time()
        delta = cur_time - self.cur_time if self.cur_time is not None else 0
        print("delta: ", delta)
        self.cur_time = cur_time
        nex_fid = self.cur_frame_id + int(delta*self.fps)
        # self._play_video(nex_fid)
        time_st = time()
        self._play_audio(nex_fid)
        print("audio read time: ", time() - time_st)
        self.cur_frame_id = nex_fid

    def play(self):
        self.timer.start(int(600 / self.fps))

    def pause(self):
        self.timer.stop()

    def quit(self):
        self.timer.stop()

    def jump_to(self, sec):
        self.cur_time = None
        self.cur_frame_id = int(sec * self.fps)
        if sec >= self.tot_secs:
            self.quit()
        self.video_reader.jump2(sec)

    def mult_speed_by(self, times):
        self.fps = int(self.ini_fps * times)
        self.pause()
        self.play()

    def get_tot_secs(self):
        return self.tot_secs

    def _play_video(self, fid):
        cur_frame_id, frame = self.video_reader.get_frame(fid)
        if cur_frame_id >= 0:
            self.father.display(cur_frame_id // self.ini_fps, frame)

    def _play_audio(self, fid):
        cur_frame_id, data = self.audio_reader.get_frame(fid)
        self.stream.write(data)