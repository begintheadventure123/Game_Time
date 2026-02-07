import os
import threading
import tkinter as tk
from tkinter import ttk

from .app import run_watcher
from .config import load_config


def _resolve_path(config_path: str, path_value: str) -> str:
    if os.path.isabs(path_value):
        return path_value
    base_dir = os.path.dirname(os.path.abspath(config_path))
    return os.path.abspath(os.path.join(base_dir, path_value))


def run_panel(config_path: str) -> None:
    repo_dir = os.path.dirname(os.path.abspath(config_path))

    # Hardcoded templates for now; update these filenames as needed.
    templates = {
        "战场": [
            _resolve_path(config_path, os.path.join("assets", "zhanchang.png")),
            _resolve_path(config_path, os.path.join("assets", "zhanchang_1.png")),
        ],
        "红包": [_resolve_path(config_path, os.path.join("assets", "hongbao.png"))],
    }

    current = {"thread": None, "stop": None, "label": None}

    def set_status(msg: str) -> None:
        status_var.set(msg)
        print(f"[panel] {msg}")

    def stop_current() -> None:
        if current["stop"] is not None:
            current["stop"].set()
        if current["thread"] is not None:
            current["thread"].join(timeout=5)
        current["thread"] = None
        current["stop"] = None
        current["label"] = None

    def start_watcher(label: str) -> None:
        template_paths = templates.get(label)
        if not template_paths:
            set_status(f"Template not set for {label}")
            return
        missing = [path for path in template_paths if not os.path.exists(path)]
        if missing:
            set_status(f"Missing template(s): {', '.join(missing)}")
            return

        config = load_config(config_path)
        config.template_path = template_paths[0]
        config.template_paths = template_paths

        stop_event = threading.Event()
        thread = threading.Thread(
            target=run_watcher, args=(config, stop_event), daemon=True
        )
        current["thread"] = thread
        current["stop"] = stop_event
        current["label"] = label
        thread.start()
        set_status(f"Running: {label}")

    def on_select() -> None:
        selection = mode_var.get()
        stop_current()
        if selection:
            start_watcher(selection)
        else:
            set_status("Stopped")

    def on_stop() -> None:
        mode_var.set("")
        stop_current()
        set_status("Stopped")

    root = tk.Tk()
    root.title("Watcher Panel")
    root.attributes("-topmost", True)
    root.resizable(True, True)
    root.geometry("220x140")

    main = ttk.Frame(root, padding=10)
    main.pack(fill="both", expand=True)

    ttk.Label(main, text="选择监控类型").pack(anchor="w")

    mode_var = tk.StringVar(value="")
    ttk.Radiobutton(
        main, text="战场", value="战场", variable=mode_var, command=on_select
    ).pack(anchor="w")
    ttk.Radiobutton(
        main, text="红包", value="红包", variable=mode_var, command=on_select
    ).pack(anchor="w")

    ttk.Button(main, text="停止", command=on_stop).pack(anchor="w", pady=(6, 0))

    status_var = tk.StringVar(value="Stopped")
    ttk.Label(main, textvariable=status_var).pack(anchor="w", pady=(6, 0))

    def on_close() -> None:
        stop_current()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    set_status("Stopped")
    root.mainloop()
