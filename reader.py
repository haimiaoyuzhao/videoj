from typing import Tuple
from time import sleep
import sys
from queue import Queue
from threading import Thread
import numpy as np
import cv2
from moviepy.editor import VideoFileClip


class BaseReader:
    def __init__(self, path, maxsize=1000):
        self.datas = Queue(maxsize=maxsize)
        self.path = path
        self.maxsize = maxsize
        self.is_read_to_end = False
        self.jump2_frame_id = None
        self.need_jump = False
        self.fps = None

    def get_frame(self, frame_id=None) -> Tuple[int, np.ndarray]:
        if frame_id is not None:
            self._jump(frame_id)
        ret, cur_frame_id, data = self._read_one_frame()
        return cur_frame_id, data

    def jump2(self, sec) -> bool:
        """
        :param sec: 跳到第几秒
        :return: 是否成功
        """
        frame_id = sec * self.fps
        self._jump(frame_id)
        return True

    def _jump(self, dst_frame_id):
        ...

    def _read_one_frame(self):
        ...

    def _quit(self):
        ...

    def _default_data(self):
        ...


class VideoReader(BaseReader):
    def __init__(self, path, maxsize=1000):
        super().__init__(path, maxsize)
        # 视频的信息
        self.fps = None
        self.size = None
        self.tot_frame = None
        self._get_video_info()
        self.videoCapture = cv2.VideoCapture(self.path)

    def _get_video_info(self):
        videoCapture = cv2.VideoCapture(self.path)
        self.fps = videoCapture.get(cv2.CAP_PROP_FPS)
        self.size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.tot_frame = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        print("fps: ", self.fps)
        print("size: ", self.size)
        print("tot frame: ", self.tot_frame)
        videoCapture.release()

    def get_fps(self):
        return self.fps

    def get_size(self):
        return self.size

    def get_tot_frame(self):
        return self.tot_frame

    def _jump(self, dst_frame_id):
        self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, dst_frame_id)

    def _read_one_frame(self):
        cur_frame_id = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
        ret, frame = self.videoCapture.read()  # 读取一帧视频
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return ret, cur_frame_id, frame

    def _quit(self):
        self.videoCapture.release()

    def _default_data(self):
        return np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)


class AudioReader(BaseReader):
    def __init__(self, path, vframes, maxsize=1000):
        super().__init__(path, maxsize)
        # 视频的信息
        video = VideoFileClip(path)
        self.audio = video.audio
        self.fps = self.audio.fps
        self.nbytes = self.audio.reader.nbytes

        totalsize = int(self.fps * self.audio.duration)
        nchunks = vframes
        self.chunksize = totalsize // nchunks
        self.nchannels = self.audio.nchannels
        self.pospos = np.linspace(0, totalsize, nchunks + 1, endpoint=True, dtype=int)

        self.cur_frame_id = 0

    def _jump(self, dst_frame_id):
        self.cur_frame_id = dst_frame_id

    def _read_one_frame(self):
        i = self.cur_frame_id
        tt = (1.0 / self.fps) * np.arange(self.pospos[i], self.pospos[i + 1])
        chunk = self.audio.to_soundarray(tt, nbytes=self.nbytes, quantize=True,
                                    fps=self.fps, buffersize=self.chunksize)
        data = chunk.tobytes()
        self.cur_frame_id += 1
        return 1, self.cur_frame_id-1, data
