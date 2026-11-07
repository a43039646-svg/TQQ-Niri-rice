#!/usr/bin/env python3
"""Make the SwayNC brightness widget match the machine's backlight devices."""
from pathlib import Path
import json
import sys


def main() -> int:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".config/swaync/config.json"
    config = json.loads(config_path.read_text())
    backlight_root = Path("/sys/class/backlight")
    devices = sorted(item.name for item in backlight_root.iterdir()) if backlight_root.is_dir() else []
    widgets = config.setdefault("widgets", [])
    widget_config = config.setdefault("widget-config", {})

    if devices:
        widget_config.setdefault("backlight", {})["device"] = devices[0]
        widget_config["backlight"].setdefault("subsystem", "backlight")
        if "backlight" not in widgets:
            widgets.insert(1, "backlight")
    else:
        config["widgets"] = [widget for widget in widgets if widget != "backlight"]
        widget_config.pop("backlight", None)

    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    if devices:
        print(f"SwayNC brightness control uses {devices[0]}.")
    else:
        print("No backlight device found; SwayNC brightness control is disabled.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError) as error:
        print(f"Couldn't configure SwayNC: {error}", file=sys.stderr)
        raise SystemExit(1)
