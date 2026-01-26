import numpy as np
import mss

from .config import ROI


class ScreenCapture:
    def __init__(self) -> None:
        self._sct = mss.mss()

    def grab_roi(self, roi: ROI) -> np.ndarray:
        monitor = {
            "left": int(roi.left),
            "top": int(roi.top),
            "width": int(roi.width),
            "height": int(roi.height),
        }
        img = np.array(self._sct.grab(monitor))
        if img.shape[-1] == 4:
            img = img[:, :, :3]
        return img

    def grab_fullscreen(self) -> np.ndarray:
        monitor = self._sct.monitors[0]
        img = np.array(self._sct.grab(monitor))
        if img.shape[-1] == 4:
            img = img[:, :, :3]
        return img

    def fullscreen_offset(self) -> tuple[int, int]:
        monitor = self._sct.monitors[0]
        return int(monitor.get("left", 0)), int(monitor.get("top", 0))
