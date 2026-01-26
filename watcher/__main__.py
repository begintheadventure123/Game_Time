import argparse


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parent.add_argument("--debug", action="store_true", help="Enable debug window")
    parent.add_argument("--threshold", type=float, help="Override matching threshold")
    parent.add_argument("--interval", type=float, help="Override loop interval seconds")
    parent.add_argument("--debounce", type=int, help="Override debounce count")
    parent.add_argument("--cooldown", type=float, help="Override cooldown seconds")

    parser = argparse.ArgumentParser(
        prog="watcher", description="Screen ROI watcher with template matching"
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--debug", action="store_true", help="Enable debug window")
    parser.add_argument("--threshold", type=float, help="Override matching threshold")
    parser.add_argument("--interval", type=float, help="Override loop interval seconds")
    parser.add_argument("--debounce", type=int, help="Override debounce count")
    parser.add_argument("--cooldown", type=float, help="Override cooldown seconds")

    subparsers = parser.add_subparsers(dest="command")
    roi_parser = subparsers.add_parser("roi", parents=[parent], help="Pick ROI")
    roi_parser.set_defaults(command="roi")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "roi":
        from .roi_picker import run_roi_picker

        run_roi_picker(args.config)
        return

    from .config import load_config
    from .app import run_watcher

    config = load_config(
        args.config,
        debug_override=args.debug,
        threshold_override=args.threshold,
        interval_override=args.interval,
        debounce_override=args.debounce,
        cooldown_override=args.cooldown,
    )
    run_watcher(config)


if __name__ == "__main__":
    main()
