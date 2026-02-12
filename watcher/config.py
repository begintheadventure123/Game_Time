import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    text_only: bool


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
    provider: str
    fallback_to_local: bool
    pushover_app_token: str
    pushover_user_key: str
    telegram_bot_token: str
    telegram_chat_id: str


@dataclass
class Debug:
    enabled: bool
    show_window: bool
    show_match_box: bool
    print_score_every_n: int
    save_enabled: bool
    save_dir: str
    save_every_n: int
    save_on_match: bool


@dataclass
class Config:
    roi: ROI
    template_path: str
    template_paths: List[str]
    matching: Matching
    runtime: Runtime
    notify: Notify
    debug: Debug


DEFAULT_CONFIG: Dict[str, Any] = {
    "roi": {"left": 100, "top": 100, "width": 400, "height": 300},
    "template_path": "assets/template.png",
    "template_paths": ["assets/template.png"],
    "matching": {
        "grayscale": True,
        "method": "TM_CCOEFF_NORMED",
        "threshold": 0.90,
        "text_only": False,
    },
    "runtime": {"interval_sec": 30.0, "debounce_count": 3, "cooldown_sec": 20},
    "notify": {
        "use_toast": True,
        "beep_fallback": True,
        "title": "Watcher Alert",
        "provider": "local",
        "fallback_to_local": True,
        "pushover_app_token": "",
        "pushover_user_key": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
    },
    "debug": {
        "enabled": False,
        "show_window": True,
        "show_match_box": False,
        "print_score_every_n": 0,
        "save_enabled": False,
        "save_dir": "debug_screens",
        "save_every_n": 0,
        "save_on_match": False,
    },
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


def _resolve_template_paths(
    config_path: str, template_paths: List[str]
) -> List[str]:
    return [
        _resolve_template_path(config_path, template_path)
        for template_path in template_paths
    ]


def _resolve_path(config_path: str, path_value: str) -> str:
    if os.path.isabs(path_value):
        return path_value
    base_dir = os.path.dirname(os.path.abspath(config_path))
    return os.path.abspath(os.path.join(base_dir, path_value))


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
        text_only=bool(matching.get("text_only", False)),
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
        provider=str(notify.get("provider", "local")).lower(),
        fallback_to_local=bool(notify.get("fallback_to_local", True)),
        pushover_app_token=str(notify.get("pushover_app_token", "")),
        pushover_user_key=str(notify.get("pushover_user_key", "")),
        telegram_bot_token=str(notify.get("telegram_bot_token", "")),
        telegram_chat_id=str(notify.get("telegram_chat_id", "")),
    )

    debug_obj = Debug(
        enabled=bool(debug.get("enabled", False)),
        show_window=bool(debug.get("show_window", True)),
        show_match_box=bool(debug.get("show_match_box", True)),
        print_score_every_n=int(debug.get("print_score_every_n", 10)),
        save_enabled=bool(debug.get("save_enabled", False)),
        save_dir=_resolve_path(
            path, str(debug.get("save_dir", "debug_screens"))
        ),
        save_every_n=int(debug.get("save_every_n", 0)),
        save_on_match=bool(debug.get("save_on_match", False)),
    )

    _validate_config(path, roi_obj, matching_obj, runtime_obj, notify_obj)

    raw_template_paths = raw.get("template_paths")
    if raw_template_paths is None:
        template_paths = [
            str(raw.get("template_path", "assets/template.png"))
        ]
    else:
        if not isinstance(raw_template_paths, list):
            raise ValueError("template_paths must be a list of paths.")
        template_paths = [str(path_value) for path_value in raw_template_paths]

    template_paths = _resolve_template_paths(path, template_paths)
    missing_templates = [
        template_path
        for template_path in template_paths
        if not os.path.exists(template_path)
    ]
    if missing_templates:
        missing = ", ".join(missing_templates)
        raise FileNotFoundError(
            f"Template image(s) not found: {missing}. "
            "Update template_paths in config.yaml."
        )

    return Config(
        roi=roi_obj,
        template_path=template_paths[0],
        template_paths=template_paths,
        matching=matching_obj,
        runtime=runtime_obj,
        notify=notify_obj,
        debug=debug_obj,
    )


def _validate_config(
    config_path: str, roi: ROI, matching: Matching, runtime: Runtime, notify: Notify
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
    if notify.provider not in ("local", "pushover", "telegram"):
        raise ValueError(
            "notify.provider must be one of: local, pushover, telegram."
        )
    if notify.provider == "pushover":
        if not notify.pushover_app_token or not notify.pushover_user_key:
            raise ValueError(
                "Pushover requires notify.pushover_app_token and notify.pushover_user_key."
            )
    if notify.provider == "telegram":
        if not notify.telegram_bot_token or not notify.telegram_chat_id:
            raise ValueError(
                "Telegram requires notify.telegram_bot_token and notify.telegram_chat_id."
            )
