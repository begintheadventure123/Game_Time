# Watcher — Screen ROI Event Notifier (Windows)

A small Windows 10/11 tool that watches a screen region (ROI) and notifies you when a template image appears, using OpenCV template matching. Includes an ROI picker and a placeholder template so you can verify everything without a real screenshot.

## Quick Start (Windows PowerShell)

```powershell
# 1) Create venv
python -m venv .venv

# 2) Activate venv
.\.venv\Scripts\Activate.ps1

# 3) Install deps
pip install -r requirements.txt
```

## Pick ROI

```powershell
python -m watcher roi --config config.yaml
```

Instructions:
- Click and drag to draw the ROI rectangle.
- Press Enter to save to `config.yaml`.
- Press Esc to cancel.

## Run Watcher

```powershell
python -m watcher --config config.yaml
```

## Run Watcher (Debug)

```powershell
python -m watcher --config config.yaml --debug
```

Debug mode shows the ROI window with the current match score (press `q` to quit).

## Verify with the Placeholder Template

1) Open `assets/template.png` (double-click in File Explorer).
2) Move the image window into your ROI area.
3) The watcher should trigger a notification (toast if available, otherwise beep + console log).

## Tuning

- Threshold: how strong the match must be (0–1)
  ```powershell
  python -m watcher --config config.yaml --threshold 0.88
  ```
- Interval: how often to scan (seconds)
  ```powershell
  python -m watcher --config config.yaml --interval 0.2
  ```
- Debounce: number of consecutive hits required
  ```powershell
  python -m watcher --config config.yaml --debounce 3
  ```
- Cooldown: suppress repeat alerts for N seconds
  ```powershell
  python -m watcher --config config.yaml --cooldown 20
  ```

## Config Reference

Edit `config.yaml` to fine-tune:
- `roi.left`, `roi.top`, `roi.width`, `roi.height`
- `template_path`
- `matching.threshold`
- `runtime.interval_sec`, `runtime.debounce_count`, `runtime.cooldown_sec`
- `debug.enabled`, `debug.show_match_box`

## Troubleshooting

- **No notifications:** Lower the threshold (e.g., 0.85) or check that the template image is fully visible in the ROI.
- **ROI seems wrong:** Re-run the ROI picker and confirm the coordinates update in `config.yaml`.
- **Toast not showing:** The app will always beep and log to console. If toast fails, ensure `winotify` is installed.
- **Multi-monitor offsets:** The ROI picker uses the virtual screen. If you see offset issues, re-run the picker with the target monitor as the active display.

## Command Help

```powershell
python -m watcher --help
python -m watcher roi --help
```

## Notes

- This tool captures only the ROI on your screen.
- Ensure this usage complies with any game’s ToS.
