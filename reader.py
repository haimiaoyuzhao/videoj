from typing import Tuple
from time import time
from queue import Queue
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
    def __init__(self, path, vframes, vfps, maxsize=1000):
        super().__init__(path, maxsize)
        # 视频的信息
        video = VideoFileClip(path)
        self.audio = video.audio
        self.fps = vfps
        self.nbytes = self.audio.reader.nbytes

        totalsize = int(self.audio.fps * self.audio.duration)
        nchunks = vframes
        self.chunksize = totalsize // nchunks
        self.nchannels = self.audio.nchannels
        self.pospos = np.linspace(0, totalsize, nchunks + 1, endpoint=True, dtype=int)

        self.cur_frame_id = 0

    def _jump(self, dst_frame_id):
        self.cur_frame_id = dst_frame_id

    def _read_one_frame(self):
        i = self.cur_frame_id
        tt = (1.0 / self.audio.fps) * np.arange(self.pospos[i], self.pospos[i + 1])
        chunk = self.audio.to_soundarray(tt, nbytes=self.nbytes, quantize=True,
                                    fps=self.audio.fps, buffersize=self.chunksize)
        data = chunk.tobytes()
        self.cur_frame_id += 1
        return 1, self.cur_frame_id-1, data


if __name__ == "__main__":

    from pyaudio import PyAudio
    video_path = r"D:\HONOR Share\Backup\Videos\myphone_1E91F5A4832C\Download\xvideos.com_d0616f18c6d1d9b1d3e1c6332bd80289.mp4"
    audio_reader = AudioReader(video_path, 35007)
    p = PyAudio()  # 初始化PyAudio模块
    stream = p.open(format=p.get_format_from_width(audio_reader.nbytes),
                     channels=audio_reader.nchannels,
                     rate=audio_reader.fps, output=True)

    for i in range(1000):
        cur_time = time()
        delta = cur_time - self.cur_time if self.cur_time is not None else 0
        print("delta: ", delta)
        self.cur_time = cur_time
        nex_fid = self.cur_frame_id + int(delta * self.fps)
        # self._play_video(nex_fid)
        time_st = time()
        self._play_audio(nex_fid)
        print("audio read time: ", time() - time_st)
        self.cur_frame_id = nex_fid

        time_st = time()
        cur_frame_id, data = audio_reader.get_frame(i)
        stream.write(data)
        print(time() - time_st)