from datetime import datetime
from pathlib import Path

import cv2
import os

class VideoSaver:
    def __init__(
        self,
        save_folder: os.PathLike,
        *,
        fps: int = 0,
        width: int = 0,
        height: int = 0,
        camera: cv2.VideoCapture = None,
    ) -> None:
        self.save_folder = save_folder
        self._writer: cv2.VideoWriter = None
        self.current_file_name = None
        self.codec = cv2.VideoWriter.fourcc(*"mp4v")

        if camera is not None:
            self.fps = camera.get(cv2.CAP_PROP_FPS)
            self.width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps > 0:
            self.fps = fps

        if width > 0 and height > 0:
            self.width = width
            self.height = height

        if any(el <= 0 for el in (self.fps, self.width, self.height)):
            raise ValueError("Invalid parameters: fps, width or height below 1")

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        self.init_new_writer()

    def _get_save_file_path(self) -> Path:
        day_today = datetime.now().strftime("%Y-%m-%d")
        hour_now = datetime.now().strftime("%H")
        file_date = f"{day_today}_{hour_now}"
        file_path = Path(self.save_folder) / f"{file_date}.mp4"
        copy_number = 0
        while file_path.exists() and file_path != self.current_file_name:
            copy_number += 1
            file_path = (
                Path(self.save_folder) / f"{file_date}(copy {copy_number}).mp4"
            )
        return file_path

    def init_new_writer(self) -> None:
        self.release()

        self.current_file_name = self._get_save_file_path()
        self._writer = cv2.VideoWriter(
            filename=str(self.current_file_name),
            fourcc=self.codec,
            fps=self.fps,
            frameSize=(self.width, self.height),
        )

    def save(self, frame: cv2.typing.MatLike) -> None:
        current_file_name = self._get_save_file_path()
        if current_file_name != self.current_file_name:
            self.init_new_writer()

        self._writer.write(frame)

    def release(self) -> None:
        if self._writer is not None and self._writer.isOpened():
            self._writer.release()
            self._writer = None

    def __del__(self) -> None:
        self.release()
