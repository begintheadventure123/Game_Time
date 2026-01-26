from __future__ import annotations

import time


def send_notification(
    *,
    title: str,
    message: str,
    use_toast: bool = True,
    beep_fallback: bool = True,
) -> None:
    notified = False

    if use_toast:
        try:
            from winotify import Notification, audio

            toast = Notification(app_id="Watcher", title=title, msg=message, duration="short")
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            notified = True
        except Exception as exc:
            print(f"[notify] Toast failed: {exc}")

    if beep_fallback:
        try:
            import winsound

            winsound.Beep(1000, 250)
            time.sleep(0.05)
            winsound.Beep(1200, 250)
            notified = True
        except Exception as exc:
            print(f"[notify] Beep failed: {exc}")

    if not notified:
        print(f"[notify] {title}: {message}")
    else:
        print(f"[notify] {title}: {message}")
