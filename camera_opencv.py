import os
import cv2
import time
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    no_camera_image = open('no_camera.jpg', 'rb').read()

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        while True:
            try:
                camera = cv2.VideoCapture(Camera.video_source)
                if not camera.isOpened():
                    yield Camera.no_camera_image
                else:
                    # read current frame
                    _, img = camera.read()
                    # encode as a jpeg image and return it
                    yield cv2.imencode('.jpg', img)[1].tobytes()
            except cv2.error:
                yield Camera.no_camera_image
            finally:
                camera.release()
