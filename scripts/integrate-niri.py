#!/usr/bin/env python3
"""Add TQQ startup commands and free keybindings without replacing Niri settings."""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


def find_block_end(text: str, opening: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    line_comment = False
    block_comment = False
    index = opening
    while index < len(text):
        char = text[index]
        pair = text[index:index + 2]
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if pair == "*/":
                block_comment = False
                index += 1
        elif quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif pair == "//":
            line_comment = True
            index += 1
        elif pair == "/*":
            block_comment = True
            index += 1
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError("Niri config has an unclosed block")


def normalize_key(key: str) -> tuple[str, ...]:
    parts = key.split("+")
    modifiers = {"Super" if part == "Mod" else "Control" if part == "Ctrl" else part for part in parts[:-1]}
    return tuple(sorted(modifiers) + [parts[-1]])


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} NIRI_CONFIG LOCAL_BIN_DIR", file=sys.stderr)
        return 2

    config_path = Path(sys.argv[1])
    local_bin = Path(sys.argv[2])
    text = config_path.read_text() if config_path.exists() else ""

    # Remove only previously generated TQQ blocks. Every user setting and bind stays intact.
    text = re.sub(
        r"(?ms)^// BEGIN TQQ NIRI STARTUP\n.*?^// END TQQ NIRI STARTUP[ \t]*(?:\n|$)",
        "",
        text,
    )
    text = re.sub(
        r"(?ms)^[ \t]*// BEGIN TQQ NIRI BINDS\n.*?^[ \t]*// END TQQ NIRI BINDS[ \t]*(?:\n|$)",
        "",
        text,
    )

    binds_match = re.search(r"(?m)^([ \t]*)binds[ \t]*\{", text)
    if binds_match:
        opening = text.find("{", binds_match.start())
        closing = find_block_end(text, opening)
        binds_body = text[opening + 1:closing]
    else:
        binds_body = ""

    # Niri binds begin with a key chord; action flags may follow before the action block.
    used = {
        normalize_key(match.group(1))
        for match in re.finditer(
            r"(?m)^[ \t]*([A-Za-z0-9_+.-]+)[ \t]*(?:[^\n{}]*)\{",
            binds_body,
        )
        if "+" in match.group(1)
    }

    def choose(candidates: list[str]) -> str:
        for candidate in candidates:
            if normalize_key(candidate) not in used:
                used.add(normalize_key(candidate))
                return candidate
        raise ValueError("No free keybinding among: " + ", ".join(candidates))

    wallpaper_key = choose(["Mod+W", "Mod+Shift+W", "Mod+Alt+W"])
    power_key = choose(["Mod+E", "Mod+Shift+E", "Mod+Alt+E"])
    launcher_key = choose(["Mod+D", "Mod+Space", "Mod+R", "Mod+Shift+D"])

    wallpaper = json.dumps(str(local_bin / "select-wallpaper"), ensure_ascii=False)
    power = json.dumps(str(local_bin / "power-menu"), ensure_ascii=False)
    managed_binds = (
        "\n    // BEGIN TQQ NIRI BINDS\n"
        f"    {wallpaper_key} {{ spawn {wallpaper}; }}\n"
        f"    {power_key} {{ spawn {power}; }}\n"
        f"    {launcher_key} {{ spawn \"fuzzel\"; }}\n"
        "    // END TQQ NIRI BINDS\n"
    )
    if binds_match:
        text = text[:closing] + managed_binds + text[closing:]
    else:
        text = text.rstrip() + "\n\nbinds {" + managed_binds + "}\n"

    startup_entries = []
    for app in ("waybar", "swaync"):
        if not re.search(
            r"(?m)^\s*(?:spawn-at-startup|spawn-sh-at-startup)\b[^\n]*\b" + app + r"\b",
            text,
        ):
            startup_entries.append(f"spawn-at-startup {json.dumps(app)}")
    restore_cmd = json.dumps(str(local_bin / "select-wallpaper"), ensure_ascii=False)
    if not re.search(r"(?m)^\s*spawn-at-startup\s+\"[^\"]*select-wallpaper\"[^\n]*--restore", text):
        startup_entries.append(f"spawn-at-startup {restore_cmd} \"--restore\"")
    if startup_entries:
        startup_block = (
            "// BEGIN TQQ NIRI STARTUP\n"
            + "\n".join(startup_entries)
            + "\n// END TQQ NIRI STARTUP\n\n"
        )
        binds_match = re.search(r"(?m)^([ \t]*)binds[ \t]*\{", text)
        insertion = binds_match.start() if binds_match else len(text)
        text = text[:insertion] + startup_block + text[insertion:]

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text)
    print(
        "Preserved the existing Niri config and added TQQ binds: "
        f"{wallpaper_key} (wallpaper), {power_key} (power), {launcher_key} (Fuzzel)."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Niri integration failed: {error}", file=sys.stderr)
        raise SystemExit(1)
