# Watcher App Plan (Windows) — Screen ROI Event Notifier (Template Matching MVP)

## 0. Overview

### Goal
Build a simple, reliable Windows app that monitors a defined region-of-interest (ROI) on the screen. When a specific game event appears (popup/icon), the app notifies the user.

### Non-Goals / Boundaries
- No process injection, memory reading, hooking, or interaction with the game process.
- No cheating automation (no input automation, no aim assist, etc.).
- Default detection is **OpenCV template matching** (not OCR by default). OCR is an optional extension.

### Key Constraints
- Runs on Windows 10/11.
- Simple deliverable: runnable from source (`python -m watcher`) and optionally packaged to `.exe`.
- Must be verifiable using a placeholder template image before real event screenshot exists.

---

## 1. User Experience (MVP)

### Primary Flows
1) Pick ROI
- Command: `python -m watcher roi --config config.yaml`
- App shows a fullscreen screenshot and lets user click-and-drag a rectangle.
- Saves ROI back into config file.

2) Run watcher
- Command: `python -m watcher --config config.yaml`
- Runs in a loop:
  - Captures ROI repeatedly
  - Computes match score against template
  - Applies debounce + cooldown
  - Sends notification when event is detected

3) Debug mode
- Flag: `--debug`
- Shows a live ROI window with match score overlay and optionally a box for best match position.

### Verification Flow (No real event yet)
- Use the placeholder `assets/template.png`
- Open that image on screen and move it inside ROI
- Confirm app triggers notification

---

## 2. Architecture

### Modules
- config: load/validate config.yaml + CLI overrides
- capture: screen capture using `mss` for ROI
- matcher: template matching using OpenCV `matchTemplate`
- notify: Windows notification (toast if possible; beep fallback)
- roi_picker: interactive ROI selection using OpenCV mouse callbacks
- app: main loop, orchestrates capture+match+debounce+notify
- __main__: CLI entrypoint

### Detection Strategy (Default)
- Use grayscale matching by default (more robust).
- `cv2.matchTemplate(..., TM_CCOEFF_NORMED)` to compute similarity score.
- Trigger when:
  - score >= threshold for N consecutive frames (debounce)
  - not in cooldown window

---

## 3. Repo Structure (Required)

Create this structure:

- watcher/
  - __init__.py
  - __main__.py
  - app.py
  - config.py
  - capture.py
  - matcher.py
  - notify.py
  - roi_picker.py
- assets/
  - template.png
- config.yaml
- requirements.txt
- README.md
- .gitignore (Python defaults)

---

## 4. Dependencies

### Required
- mss
- numpy
- opencv-python
- PyYAML

### Optional (toast)
Choose a lightweight Windows toast library. Options:
- `winotify` (simple)
- or `plyer` (cross-platform notifications, but sometimes flaky on Windows)
- or fallback only (winsound beep + console)

Priority: reliability. If toast is troublesome, beep must always work.

---

## 5. Config Spec (config.yaml)

A default config.yaml must exist and allow app to run out-of-the-box.

Example:

```yaml
roi:
  left: 100
  top: 100
  width: 400
  height: 300

template_path: "assets/template.png"

matching:
  grayscale: true
  method: "TM_CCOEFF_NORMED"
  threshold: 0.90

runtime:
  interval_sec: 0.30
  debounce_count: 3
  cooldown_sec: 20

notify:
  use_toast: true
  beep_fallback: true
  title: "Watcher Alert"

debug:
  enabled: false
  show_match_box: true
  print_score_every_n: 10
```

### CLI overrides
Support overrides like:
- `--config config.yaml`
- `--debug`
- `--threshold 0.88`
- `--interval 0.2`

---

## 6. Implementation Details (Step-by-step)

### Step A — Skeleton + CLI
- Implement argparse with subcommands:
  - `watcher` (default run)
  - `watcher roi` (ROI picker)
- `python -m watcher --help` works.

### Step B — Config Loader
- `watcher/config.py`:
  - Load YAML into dataclasses or dict with validation.
  - Validate ROI values are positive.
  - Validate template path exists (friendly error with instructions).
  - Merge CLI overrides.

### Step C — Screen Capture
- `watcher/capture.py`:
  - Use `mss.mss().grab(monitor)` to capture ROI.
  - Return BGR image (numpy array) compatible with OpenCV.

Performance target:
- ROI capture every 0.2~0.5 sec is enough for popups.

### Step D — Template Matching
- `watcher/matcher.py`:
  - Load template once at startup.
  - In loop: convert frame (and template) to grayscale if configured.
  - `cv2.matchTemplate(frame, template, method)`
  - Use `cv2.minMaxLoc` to get max score and location.
  - Return (score, loc).

Optional robustness:
- Allow scale factor(s) list, e.g. [1.0, 0.9, 1.1] to handle minor scaling changes (but keep MVP simple).

### Step E — Debounce + Cooldown
Implement in `watcher/app.py`:
- maintain `hit_streak`:
  - if score >= threshold => hit_streak += 1 else reset to 0
- trigger when `hit_streak >= debounce_count` and not in cooldown
- cooldown:
  - `cooldown_until = now + cooldown_sec`
  - ignore triggers until cooldown ends

Log behavior:
- print score occasionally
- print trigger events with timestamp and score
- print cooldown end

### Step F — Notification
- `watcher/notify.py`:
  - Try toast notification if `use_toast` true
  - If toast fails OR library missing:
    - fallback beep: `winsound.Beep(1000, 300)` x 2
    - print to console

Ensure notify never crashes the loop.

### Step G — Debug UI
When debug enabled:
- show ROI window with:
  - overlay score text (`cv2.putText`)
  - optional rectangle at best match location within ROI
- allow `q` key to quit

### Step H — ROI Picker
- `watcher/roi_picker.py`:
  - take fullscreen screenshot using mss
  - show in OpenCV window
  - implement mouse callback:
    - on LButtonDown record start
    - on mouse move draw rectangle overlay
    - on LButtonUp finalize rectangle
  - confirm with Enter:
    - write ROI values to config.yaml (preserve other keys)
  - Esc cancels

Coordinates:
- ROI is in absolute screen pixels.

### Step I — README
Include:
- Setup: venv + pip install
- ROI picker usage
- Running watcher
- Debug usage
- How to replace template with real event screenshot
- How to tune threshold and ROI
- Troubleshooting common issues

---

## 7. Placeholder Template Generation

The repo must include a valid `assets/template.png` so verification is possible without real screenshot.

Approach:
- Generate a simple image with a distinctive pattern (e.g., a white box with a black border and a symbol) and save as PNG during repo creation OR commit a static PNG.

Verification:
- User opens assets/template.png on screen and moves it into the ROI.

---

## 8. Acceptance Criteria (Definition of Done)

### MUST
1) `pip install -r requirements.txt` succeeds on Windows.
2) `python -m watcher roi --config config.yaml` updates ROI in config.
3) `python -m watcher --config config.yaml --debug` shows ROI live window.
4) When placeholder template appears in ROI, app triggers:
   - at least beep OR toast
   - respects debounce and cooldown
5) Clean exit on Ctrl+C and/or 'q' in debug window.
6) README is sufficient for a fresh user to run end-to-end.

### NICE TO HAVE
- PyInstaller packaging to exe
- multi-monitor support (document limitations)
- optional OCR extension (future)

---

## 9. Safety / Compliance Notes (Important)
- Only uses screen capture of ROI.
- No direct game process access.
- User should ensure this does not violate game ToS; this tool is a personal notification assistant.

---

## 10. Future Extensions (Optional)
- OCR mode for text-based events (PaddleOCR/EasyOCR).
- Multi-template support (multiple events).
- Remote notification (Discord/Telegram/Pushover).
- Auto-calibration threshold (collect scores when idle vs event).
- Scale-invariant matching and/or feature-based matching (ORB/SIFT alternatives).
