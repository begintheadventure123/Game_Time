from typing import Tuple

import cv2
import numpy as np


class TemplateMatcher:
    def __init__(self, template_path: str, grayscale: bool, method_name: str) -> None:
        self.grayscale = grayscale
        self.method_name = method_name
        self.method = getattr(cv2, method_name, cv2.TM_CCOEFF_NORMED)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Failed to load template image: {template_path}")
        if self.grayscale:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.template = template
        self.template_height, self.template_width = template.shape[:2]

    def match(self, frame: np.ndarray) -> Tuple[float, Tuple[int, int]]:
        image = frame
        if self.grayscale:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(image, self.template, self.method)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
        return float(max_val), (int(max_loc[0]), int(max_loc[1]))

    def template_size(self) -> Tuple[int, int]:
        return self.template_width, self.template_height
