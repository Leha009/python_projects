import cv2
import os
import signal

from video_saver import VideoSaver

RUNNING = True

def signal_handler(signal, frame) -> None:
    global RUNNING
    RUNNING = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

RTSP_URL = os.getenv("RTSP_URL")
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "./records/")
TARGER_FPS = int(os.getenv("TARGET_FPS", 24))

if not RTSP_URL.strip():
    raise ValueError("RTSP_URL is not set")

CAMERA = cv2.VideoCapture(RTSP_URL)
VIDEO_SAVER = VideoSaver(SAVE_FOLDER, fps=24, camera=CAMERA)

try:
    while RUNNING and CAMERA.isOpened():
        ret, frame = CAMERA.read()
        if not ret:
            continue

        VIDEO_SAVER.save(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    CAMERA.release()
    VIDEO_SAVER.release()
