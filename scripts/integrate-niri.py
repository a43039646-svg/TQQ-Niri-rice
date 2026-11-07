#!/usr/bin/env python3
"""Write the complete TQQ Niri config after install.sh backs up the old one."""
from __future__ import annotations

from pathlib import Path
import json
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} NIRI_CONFIG LOCAL_BIN_DIR", file=sys.stderr)
        return 2

    config_path = Path(sys.argv[1])
    local_bin = Path(sys.argv[2])
    wallpaper = json.dumps(str(local_bin / "select-wallpaper"), ensure_ascii=False)
    power = json.dumps(str(local_bin / "power-menu"), ensure_ascii=False)
    config = f'''// TQQ Niri Rice configuration.
// The previous config is kept in the installer's dated backup directory.

spawn-at-startup "waybar"
spawn-at-startup "swaync"
spawn-at-startup {wallpaper} "--restore"

binds {{
    // Rice controls
    Mod+W {{ spawn {wallpaper}; }}
    Mod+E {{ spawn {power}; }}
    Mod+D {{ spawn "fuzzel"; }}

    // Window and workspace navigation
    Mod+Q {{ close-window; }}
    Mod+Left {{ focus-column-left; }}
    Mod+Right {{ focus-column-right; }}
    Mod+Up {{ focus-workspace-up; }}
    Mod+Down {{ focus-workspace-down; }}
    Mod+Shift+Left {{ move-column-left; }}
    Mod+Shift+Right {{ move-column-right; }}
}}
'''
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config)
    print(f"Wrote the TQQ Niri config to {config_path}; the previous config must be backed up before calling this helper.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError as error:
        print(f"Could not write Niri config: {error}", file=sys.stderr)
        raise SystemExit(1)
