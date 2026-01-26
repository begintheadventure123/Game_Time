import cv2

from .capture import ScreenCapture
from .config import read_config_dict, write_config_dict


class _ROISelector:
    def __init__(self, image, offset_left: int, offset_top: int) -> None:
        self.image = image
        self.offset_left = offset_left
        self.offset_top = offset_top
        self.start = None
        self.end = None
        self.dragging = False

    def on_mouse(self, event, x, y, _flags, _param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
            self.end = (x, y)
            self.dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.end = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.end = (x, y)
            self.dragging = False

    def has_selection(self) -> bool:
        return self.start is not None and self.end is not None

    def rect(self):
        if not self.has_selection():
            return None
        x1, y1 = self.start
        x2, y2 = self.end
        left = min(x1, x2) + self.offset_left
        top = min(y1, y2) + self.offset_top
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        return left, top, width, height

    def draw(self):
        display = self.image.copy()
        if self.has_selection():
            x1, y1 = self.start
            x2, y2 = self.end
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return display


def run_roi_picker(config_path: str) -> None:
    capture = ScreenCapture()
    screenshot = capture.grab_fullscreen()
    offset_left, offset_top = capture.fullscreen_offset()

    selector = _ROISelector(screenshot, offset_left, offset_top)
    window_name = "Select ROI - Drag mouse, Enter=Save, Esc=Cancel"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, selector.on_mouse)

    try:
        while True:
            display = selector.draw()
            cv2.imshow(window_name, display)
            key = cv2.waitKey(20) & 0xFF
            if key == 27:  # Esc
                print("[roi] Cancelled.")
                return
            if key in (10, 13):  # Enter
                if not selector.has_selection():
                    print("[roi] No selection made.")
                    continue
                left, top, width, height = selector.rect()
                if width <= 0 or height <= 0:
                    print("[roi] Invalid selection.")
                    continue
                data = read_config_dict(config_path)
                data.setdefault("roi", {})
                data["roi"]["left"] = int(left)
                data["roi"]["top"] = int(top)
                data["roi"]["width"] = int(width)
                data["roi"]["height"] = int(height)
                write_config_dict(config_path, data)
                print(
                    f"[roi] Saved ROI to {config_path}: "
                    f"left={left}, top={top}, width={width}, height={height}"
                )
                return
    finally:
        cv2.destroyAllWindows()
