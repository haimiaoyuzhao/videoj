import numpy as np
from threading import Thread
from PyQt5.QtCore import QTimer
from abc import abstractmethod
from time import time

from moviepy.editor import VideoFileClip
from pyaudio import PyAudio

from reader import VideoReader


class BasePlayer:
    def __init__(self):
        ...

    @abstractmethod
    def play(self):
        ...

    @abstractmethod
    def pause(self):
        ...

    @abstractmethod
    def quit(self):
        ...

    @abstractmethod
    def jump_to(self, sec):
        ...

    @abstractmethod
    def mult_speed_by(self, times):
        ...


class VideoPlayer(BasePlayer):
    def __init__(self, window, video_path, father):
        super(VideoPlayer, self).__init__()
        self.father = father
        self.window = window
        self.video_reader = VideoReader(video_path)
        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self._play_frame)  # 到达设定的时间后，执行槽函数代码

        self.ini_fps = int(self.video_reader.get_fps())  # 视频自带的fps值
        self.fps = self.ini_fps  # 当前视频读取软件设置的fps值，因为有加速，所以跟上一个并不总是相等
        self.cur_frame_id = 0
        self.cur_time = None

        self.tot_frame = int(self.video_reader.get_tot_frame())
        self.tot_secs = self.tot_frame // self.ini_fps

    def _play_frame(self):
        if self.video_reader is not None:
            # print("play start")
            cur_time = time()
            delta = cur_time - self.cur_time if self.cur_time is not None else 0
            self.cur_time = cur_time
            nex_fid = self.cur_frame_id + int(delta*self.fps)
            self.cur_frame_id, frame = self.video_reader.get_frame(nex_fid)
            self.cur_frame_id = nex_fid
            if self.cur_frame_id >= 0:
                self.father.display(self.cur_frame_id//self.ini_fps, frame)
            from time import sleep
            # print("play end")

    def play(self):
        self.timer.start(int(1000 / self.fps))
        # timer = Timer(1 / self.fps, self._play_frame)
        # timer.start()

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


class AudioPlayer(BasePlayer):
    def __init__(self, path, maxsize=200):
        super(AudioPlayer, self).__init__()
        video = VideoFileClip(path)
        self.audio = video.audio

        self.maxsize = maxsize
        self.cur_frame_id = 0
        self.state = 0  # 0代表stop 1 代表start
        self.fps = 4410
        p = PyAudio()  # 初始化PyAudio模块
        self.stream = p.open(format=p.get_format_from_width(self.audio.reader.nbytes),
                             channels=self.audio.nchannels,
                             rate=self.fps, output=True)
        self.thread = Thread(target=self._play_frame)
        self.thread.setDaemon(True)
        self.thread.start()

    def play(self):
        self.state = 1
        if self.stream.is_stopped():
            self.stream.start_stream()

    def pause(self):
        self.state = 0
        if not self.stream.is_stopped():
            self.stream.stop_stream()

    def quit(self):
        self.pause()
        self.stream.close()

    def _play_frame(self):
        audio = self.audio
        nbytes = audio.reader.nbytes
        fps = self.fps
        totalsize = int(fps * audio.duration)
        chunksize = 1000
        nchunks = totalsize // chunksize + 1

        pospos = np.linspace(0, totalsize, nchunks + 1, endpoint=True, dtype=int)
        while self.cur_frame_id < nchunks:
            if self.state == 0:
                continue
            # time_st = time.time()
            i = self.cur_frame_id
            tt = (1.0 / fps) * np.arange(pospos[i], pospos[i + 1])
            chunk = audio.to_soundarray(tt, nbytes=nbytes, quantize=True,
                                      fps=fps, buffersize=chunksize)
            data = chunk.tobytes()
            self.stream.write(data)
            self.cur_frame_id += 1
            # print(time.time() - time_st)

    def jump_to(self, sec):
        pass

    def mult_speed_by(self, times):
        pass


if __name__ == "__main__":
    audio_player = AudioPlayer(
        r'D:\HONOR Share\Backup\Videos\myphone_1E91F5A4832C\Download\xvideos.com_d0616f18c6d1d9b1d3e1c6332bd80289.mp4')
    audio_player.play()
