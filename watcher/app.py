import time
import cv2

from .capture import ScreenCapture
from .config import Config
from .matcher import TemplateMatcher
from .notify import send_notification


def run_watcher(config: Config) -> None:
    capture = ScreenCapture()
    matcher = TemplateMatcher(
        config.template_path,
        config.matching.grayscale,
        config.matching.method,
    )

    hit_streak = 0
    cooldown_until = 0.0
    frame_index = 0

    print("[watcher] Starting watcher loop...")

    try:
        while True:
            frame = capture.grab_roi(config.roi)
            score, loc = matcher.match(frame)
            frame_index += 1

            if score >= config.matching.threshold:
                hit_streak += 1
            else:
                hit_streak = 0

            now = time.time()
            if hit_streak >= config.runtime.debounce_count and now >= cooldown_until:
                message = f"Match score {score:.3f}"
                send_notification(
                    title=config.notify.title,
                    message=message,
                    use_toast=config.notify.use_toast,
                    beep_fallback=config.notify.beep_fallback,
                )
                cooldown_until = now + config.runtime.cooldown_sec
                hit_streak = 0
                if config.runtime.cooldown_sec > 0:
                    print(
                        f"[watcher] Cooldown for {config.runtime.cooldown_sec:.1f}s"
                    )

            if config.debug.print_score_every_n > 0:
                if frame_index % config.debug.print_score_every_n == 0:
                    print(f"[watcher] score={score:.4f} streak={hit_streak}")

            if config.debug.enabled:
                display = frame.copy()
                if config.debug.show_match_box:
                    w, h = matcher.template_size()
                    top_left = loc
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    cv2.rectangle(display, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(
                    display,
                    f"score: {score:.3f}",
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

            time.sleep(config.runtime.interval_sec)
    except KeyboardInterrupt:
        print("[watcher] Stopped by Ctrl+C.")
    finally:
        if config.debug.enabled:
            cv2.destroyAllWindows()
        print("[watcher] Exiting.")
