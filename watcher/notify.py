from __future__ import annotations

import time
import urllib.parse
import urllib.request


def _post_form(url: str, payload: dict[str, str], timeout: float = 10.0) -> None:
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()


def _send_pushover(*, title: str, message: str, app_token: str, user_key: str) -> None:
    _post_form(
        "https://api.pushover.net/1/messages.json",
        {"token": app_token, "user": user_key, "title": title, "message": message},
    )


def _send_telegram(*, title: str, message: str, bot_token: str, chat_id: str) -> None:
    _post_form(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        {"chat_id": chat_id, "text": f"{title}: {message}"},
    )


def send_notification(
    *,
    title: str,
    message: str,
    use_toast: bool = True,
    beep_fallback: bool = True,
    provider: str = "local",
    fallback_to_local: bool = True,
    pushover_app_token: str = "",
    pushover_user_key: str = "",
    telegram_bot_token: str = "",
    telegram_chat_id: str = "",
) -> None:
    notified = False

    provider = (provider or "local").lower()

    if provider == "pushover":
        try:
            _send_pushover(
                title=title,
                message=message,
                app_token=pushover_app_token,
                user_key=pushover_user_key,
            )
            notified = True
        except Exception as exc:
            print(f"[notify] Pushover failed: {exc}")
    elif provider == "telegram":
        try:
            _send_telegram(
                title=title,
                message=message,
                bot_token=telegram_bot_token,
                chat_id=telegram_chat_id,
            )
            notified = True
        except Exception as exc:
            print(f"[notify] Telegram failed: {exc}")

    if not notified and fallback_to_local and use_toast:
        try:
            from winotify import Notification, audio

            toast = Notification(app_id="Watcher", title=title, msg=message, duration="short")
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            notified = True
        except Exception as exc:
            print(f"[notify] Toast failed: {exc}")

    if not notified and fallback_to_local and beep_fallback:
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
