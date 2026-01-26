import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import yaml


@dataclass
class ROI:
    left: int
    top: int
    width: int
    height: int


@dataclass
class Matching:
    grayscale: bool
    method: str
    threshold: float


@dataclass
class Runtime:
    interval_sec: float
    debounce_count: int
    cooldown_sec: float


@dataclass
class Notify:
    use_toast: bool
    beep_fallback: bool
    title: str


@dataclass
class Debug:
    enabled: bool
    show_match_box: bool
    print_score_every_n: int


@dataclass
class Config:
    roi: ROI
    template_path: str
    matching: Matching
    runtime: Runtime
    notify: Notify
    debug: Debug


DEFAULT_CONFIG: Dict[str, Any] = {
    "roi": {"left": 100, "top": 100, "width": 400, "height": 300},
    "template_path": "assets/template.png",
    "matching": {
        "grayscale": True,
        "method": "TM_CCOEFF_NORMED",
        "threshold": 0.90,
    },
    "runtime": {"interval_sec": 0.30, "debounce_count": 3, "cooldown_sec": 20},
    "notify": {
        "use_toast": True,
        "beep_fallback": True,
        "title": "Watcher Alert",
    },
    "debug": {"enabled": False, "show_match_box": True, "print_score_every_n": 10},
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_config_dict(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file not found: {path}. Create it or pass --config."
        )
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def write_config_dict(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def _resolve_template_path(config_path: str, template_path: str) -> str:
    if os.path.isabs(template_path):
        return template_path
    base_dir = os.path.dirname(os.path.abspath(config_path))
    return os.path.abspath(os.path.join(base_dir, template_path))


def load_config(
    path: str,
    *,
    debug_override: Optional[bool] = None,
    threshold_override: Optional[float] = None,
    interval_override: Optional[float] = None,
    debounce_override: Optional[int] = None,
    cooldown_override: Optional[float] = None,
) -> Config:
    raw = _deep_merge(DEFAULT_CONFIG, read_config_dict(path))

    if debug_override is True:
        raw.setdefault("debug", {})["enabled"] = True
    if threshold_override is not None:
        raw.setdefault("matching", {})["threshold"] = float(threshold_override)
    if interval_override is not None:
        raw.setdefault("runtime", {})["interval_sec"] = float(interval_override)
    if debounce_override is not None:
        raw.setdefault("runtime", {})["debounce_count"] = int(debounce_override)
    if cooldown_override is not None:
        raw.setdefault("runtime", {})["cooldown_sec"] = float(cooldown_override)

    roi = raw.get("roi", {})
    matching = raw.get("matching", {})
    runtime = raw.get("runtime", {})
    notify = raw.get("notify", {})
    debug = raw.get("debug", {})

    roi_obj = ROI(
        left=int(roi.get("left", 0)),
        top=int(roi.get("top", 0)),
        width=int(roi.get("width", 0)),
        height=int(roi.get("height", 0)),
    )

    matching_obj = Matching(
        grayscale=bool(matching.get("grayscale", True)),
        method=str(matching.get("method", "TM_CCOEFF_NORMED")),
        threshold=float(matching.get("threshold", 0.9)),
    )

    runtime_obj = Runtime(
        interval_sec=float(runtime.get("interval_sec", 0.3)),
        debounce_count=int(runtime.get("debounce_count", 3)),
        cooldown_sec=float(runtime.get("cooldown_sec", 20)),
    )

    notify_obj = Notify(
        use_toast=bool(notify.get("use_toast", True)),
        beep_fallback=bool(notify.get("beep_fallback", True)),
        title=str(notify.get("title", "Watcher Alert")),
    )

    debug_obj = Debug(
        enabled=bool(debug.get("enabled", False)),
        show_match_box=bool(debug.get("show_match_box", True)),
        print_score_every_n=int(debug.get("print_score_every_n", 10)),
    )

    _validate_config(path, roi_obj, matching_obj, runtime_obj)

    template_path = _resolve_template_path(
        path, str(raw.get("template_path", "assets/template.png"))
    )
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Template image not found: {template_path}. "
            "Update template_path in config.yaml."
        )

    return Config(
        roi=roi_obj,
        template_path=template_path,
        matching=matching_obj,
        runtime=runtime_obj,
        notify=notify_obj,
        debug=debug_obj,
    )


def _validate_config(
    config_path: str, roi: ROI, matching: Matching, runtime: Runtime
) -> None:
    if roi.width <= 0 or roi.height <= 0:
        raise ValueError("ROI width/height must be positive.")
    if roi.left < 0 or roi.top < 0:
        raise ValueError("ROI left/top must be non-negative.")
    if not (0.0 <= matching.threshold <= 1.0):
        raise ValueError("matching.threshold must be between 0 and 1.")
    if runtime.interval_sec <= 0:
        raise ValueError("runtime.interval_sec must be > 0.")
    if runtime.debounce_count < 1:
        raise ValueError("runtime.debounce_count must be >= 1.")
    if runtime.cooldown_sec < 0:
        raise ValueError("runtime.cooldown_sec must be >= 0.")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
