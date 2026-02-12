import os
import time
from threading import Event
from typing import Optional

import cv2

from .capture import ScreenCapture
from .config import Config
from .matcher import TemplateMatcher
from .notify import send_notification


def run_watcher(config: Config, stop_event: Optional[Event] = None) -> None:
    capture = ScreenCapture()
    matchers = [
        TemplateMatcher(
            template_path,
            config.matching.grayscale,
            config.matching.method,
            config.matching.text_only,
        )
        for template_path in config.template_paths
    ]

    hit_streak = 0
    cooldown_until = 0.0
    frame_index = 0

    print("[watcher] Starting watcher loop...")
    if config.debug.save_enabled:
        os.makedirs(config.debug.save_dir, exist_ok=True)
        print(f"[watcher] Saving frames to: {config.debug.save_dir}")

    try:
        while True:
            if stop_event is not None and stop_event.is_set():
                print("[watcher] Stop requested.")
                break
            frame = capture.grab_roi(config.roi)
            best_score = -1.0
            best_loc = (0, 0)
            best_matcher = matchers[0]
            for matcher in matchers:
                score, loc = matcher.match(frame)
                if score > best_score:
                    best_score = score
                    best_loc = loc
                    best_matcher = matcher
            frame_index += 1
            saved_frame = False

            if config.debug.save_enabled and config.debug.save_every_n > 0:
                if frame_index % config.debug.save_every_n == 0:
                    ts = time.strftime("%Y%m%d-%H%M%S")
                    filename = (
                        f"frame_{ts}_{frame_index:06d}_{best_score:.3f}.png"
                    )
                    path = os.path.join(config.debug.save_dir, filename)
                    cv2.imwrite(path, frame)
                    saved_frame = True
                    print(f"[watcher] saved {path}")

            if best_score >= config.matching.threshold:
                hit_streak += 1
            else:
                hit_streak = 0

            now = time.time()
            if hit_streak >= config.runtime.debounce_count and now >= cooldown_until:
                message = f"Match score {best_score:.3f}"
                send_notification(
                    title=config.notify.title,
                    message=message,
                    use_toast=config.notify.use_toast,
                    beep_fallback=config.notify.beep_fallback,
                    provider=config.notify.provider,
                    fallback_to_local=config.notify.fallback_to_local,
                    pushover_app_token=config.notify.pushover_app_token,
                    pushover_user_key=config.notify.pushover_user_key,
                    telegram_bot_token=config.notify.telegram_bot_token,
                    telegram_chat_id=config.notify.telegram_chat_id,
                )
                if config.debug.save_enabled and config.debug.save_on_match:
                    if not saved_frame:
                        ts = time.strftime("%Y%m%d-%H%M%S")
                        filename = (
                            f"match_{ts}_{frame_index:06d}_{best_score:.3f}.png"
                        )
                        path = os.path.join(config.debug.save_dir, filename)
                        cv2.imwrite(path, frame)
                        print(f"[watcher] saved match {path}")
                cooldown_until = now + config.runtime.cooldown_sec
                hit_streak = 0
                if config.runtime.cooldown_sec > 0:
                    print(
                        f"[watcher] Cooldown for {config.runtime.cooldown_sec:.1f}s"
                    )

            if config.debug.print_score_every_n > 0:
                if frame_index % config.debug.print_score_every_n == 0:
                    print(
                        f"[watcher] score={best_score:.4f} streak={hit_streak}"
                    )

            if config.debug.enabled and config.debug.show_window:
                display = frame.copy()
                if config.debug.show_match_box:
                    w, h = best_matcher.template_size()
                    top_left = best_loc
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    cv2.rectangle(display, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(
                    display,
                    f"score: {best_score:.3f}",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("Watcher ROI", display)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    print("[watcher] Quit requested via 'q'.")
                    break

            if stop_event is not None:
                if stop_event.wait(config.runtime.interval_sec):
                    print("[watcher] Stop requested.")
                    break
            else:
                time.sleep(config.runtime.interval_sec)
    except KeyboardInterrupt:
        print("[watcher] Stopped by Ctrl+C.")
    finally:
        if config.debug.enabled and config.debug.show_window:
            cv2.destroyAllWindows()
        print("[watcher] Exiting.")
