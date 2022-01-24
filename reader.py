from typing import Tuple
from time import sleep
import sys
from queue import Queue
from threading import Thread
import numpy as np
import cv2


class BaseReader:
    def __init__(self, path, maxsize=1000):
        self.datas = Queue(maxsize=maxsize)
        self.path = path
        self.maxsize = maxsize
        self.is_read_to_end = False
        self.jump2_frame_id = None
        self.need_jump = False
        self.fps = None
        self.last_frame = -1 # 队列里最晚的frame编号
        self.old_frame = -1  # 队列里最早的frame编号

        self.thread = Thread(target=self.read)
        self.thread.setDaemon(True)

    def get_frame(self, frame_id=None) -> Tuple[int, np.ndarray]:
        # print("i need ", frame_id)
        while True:
            try:
                while not self.datas.empty():
                    cur_frame_id, img = self.datas.get()
                    self.old_frame = cur_frame_id + 1
                    # print(cur_frame_id)
                    if frame_id is None or abs(cur_frame_id - frame_id) <= 5:
                        # print("you get ", cur_frame_id)
                        return cur_frame_id, img
            except Exception as e:
                print(e)
            sleep(0.5)
        # print(frame_id, " no frame get")
        return -1, self._default_data()

    def read(self):
        try:
            while True:
                print(self.old_frame, self.last_frame)
                if self.need_jump:
                    # 如果当前队列的数据不在要跳到的帧的范围内，直接重新开一个队列
                    if not self.datas.empty():
                        if self.jump2_frame_id < self.old_frame or self.jump2_frame_id > self.last_frame:
                            print("not in")
                            self.datas = Queue(maxsize=self.maxsize)
                        else:
                            print("in")
                    if self.datas.empty():
                        # 如果队列为空，说明队列中没有想要的元素，就需要跳一下。
                        # 而如果队列不为空，说明队列中已经包含了要跳到的帧，那么继续读就好。
                        self._jump()
                        self.old_frame = self.jump2_frame_id
                    ret, cur_frame_id, data = self._read_one_frame()
                    self.need_jump = False
                else:
                    if self.datas.full():
                        continue
                    ret, cur_frame_id, data = self._read_one_frame()
                self.last_frame = cur_frame_id
                if not ret:
                    break
                self.datas.put((cur_frame_id, data))
        except Exception as e:
            print(e)
        self.need_jump = False
        self.is_read_to_end = True
        self._quit()

    def jump2(self, sec) -> bool:
        """
        :param sec: 跳到第几秒
        :return: 是否成功
        """
        try:
            frame_id = sec * self.fps
            print(__file__, sys._getframe().f_lineno, " jump to: ", frame_id)
            self.jump2_frame_id = frame_id
            self.need_jump = True
            while True:
                sleep(1)
                if not self.need_jump:
                    return True
        except Exception as e:
            print(e)
        return False

    def _jump(self):
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

        self.thread.start()

    def _get_video_info(self):
        videoCapture = cv2.VideoCapture(self.path)
        self.fps = videoCapture.get(cv2.CAP_PROP_FPS)
        self.size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.tot_frame = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
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

    def _jump(self):
        self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, self.jump2_frame_id)

    def _read_one_frame(self):
        cur_frame_id = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
        ret, frame = self.videoCapture.read()  # 读取一帧视频
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return ret, cur_frame_id, frame

    def _quit(self):
        self.videoCapture.release()

    def _default_data(self):
        return np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)