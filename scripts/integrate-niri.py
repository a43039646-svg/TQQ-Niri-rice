#!/usr/bin/env python3
"""Add TQQ startup entries and keybindings without replacing the user's Niri config."""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


def closing_brace(text: str, opening: int) -> int:
    depth = 0
    quote = False
    escaped = False
    line_comment = False
    block_comment = False
    index = opening
    while index < len(text):
        char = text[index]
        nxt = text[index:index + 2]
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if nxt == "*/":
                block_comment = False
                index += 1
        elif quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
        elif nxt == "//":
            line_comment = True
            index += 1
        elif nxt == "/*":
            block_comment = True
            index += 1
        elif char == '"':
            quote = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError("Niri config has an unclosed block")


def kdl_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} NIRI_CONFIG LOCAL_BIN_DIR", file=sys.stderr)
        return 2
    config_path = Path(sys.argv[1])
    local_bin = Path(sys.argv[2])
    text = config_path.read_text()

    # Replace only TQQ-managed sections, preserving every other Niri setting.
    text = re.sub(
        r"(?ms)^// BEGIN TQQ NIRI STARTUP\n.*?^// END TQQ NIRI STARTUP[ \t]*(?:\n|$)",
        "",
        text,
    )
    text = re.sub(
        r"(?ms)^\s*// BEGIN TQQ NIRI BINDS\n.*?^\s*// END TQQ NIRI BINDS[ \t]*(?:\n|$)",
        "",
        text,
    )
    # The TQQ picker owns the desktop wallpaper and regenerates the palette.
    # Retire direct startup commands for competing wallpaper setters, while
    # leaving the rest of the user's Niri config intact and backed up.
    text = re.sub(
        r"(?m)^[ \t]*(?:spawn-at-startup|spawn-sh-at-startup)\b[^\n]*"
        r"(?:select-wallpaper|waypaper|swaybg|awww|swww|hyprpaper|mpvpaper)"
        r"[^\n]*(?:\n|$)",
        "",
        text,
    )

    binds_match = re.search(r"(?m)^([ \t]*)binds[ \t]*\{", text)
    if not binds_match:
        print(f"No top-level binds {{...}} block found in {config_path}; left it unchanged.", file=sys.stderr)
        return 1
    opening = text.find("{", binds_match.start())
    closing = closing_brace(text, opening)
    existing_binds = text[opening + 1:closing]
    def normalize_key(key: str) -> str:
        parts = key.split("+")
        trigger = parts[-1]
        modifiers = {"Super" if part == "Mod" else "Control" if part == "Ctrl" else part for part in parts[:-1]}
        return "+".join(sorted(modifiers) + [trigger])

    used = {
        normalize_key(key)
        for key in re.findall(r"(?m)^\s*([^\s{}]+(?:\+[^\s{}]+)*)[^\n{}]*\{", existing_binds)
    }

    def choose(candidates: list[str]) -> str:
        for candidate in candidates:
            normalized = normalize_key(candidate)
            if normalized not in used:
                used.add(normalized)
                return candidate
        raise ValueError("No free keybinding among: " + ", ".join(candidates))

    wallpaper_key = choose(["Super+W", "Super+Shift+W", "Super+Alt+W"])
    power_key = choose(["Super+E", "Super+Shift+E", "Super+Alt+E"])
    launcher_key = choose(["Mod+D", "Super+Space", "Super+R"])

    wallpaper_cmd = kdl_quote(str(local_bin / "select-wallpaper"))
    power_cmd = kdl_quote(str(local_bin / "power-menu"))
    rofi_cmd = kdl_quote("rofi")
    managed_binds = (
        "\n    // BEGIN TQQ NIRI BINDS\n"
        f"    {wallpaper_key} {{ spawn {wallpaper_cmd}; }}\n"
        f"    {power_key} {{ spawn {power_cmd}; }}\n"
        f"    {launcher_key} {{ spawn {rofi_cmd} \"-show\" \"drun\"; }}\n"
        "    // END TQQ NIRI BINDS\n"
    )
    text = text[:closing] + managed_binds + text[closing:]

    # Add only startup applications that are not already started in the config.
    startup_entries = []
    for app in ("waybar", "swaync"):
        if not re.search(
            r"(?m)^\s*(?:spawn-at-startup|spawn-sh-at-startup)\b[^\n]*\b" + app + r"\b",
            text,
        ):
            startup_entries.append(f"spawn-at-startup {kdl_quote(app)}")
    restore_cmd = str(local_bin / "select-wallpaper")
    startup_entries.append(f"spawn-at-startup {kdl_quote(restore_cmd)} \"--restore\"")
    if startup_entries:
        startup_block = (
            "// BEGIN TQQ NIRI STARTUP\n"
            + "\n".join(startup_entries)
            + "\n// END TQQ NIRI STARTUP\n\n"
        )
        current_binds = re.search(r"(?m)^([ \t]*)binds[ \t]*\{", text)
        text = text[:current_binds.start()] + startup_block + text[current_binds.start():]

    config_path.write_text(text)
    print(f"Added binds {wallpaper_key} (wallpaper), {power_key} (power), {launcher_key} (Rofi).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Niri integration failed: {error}", file=sys.stderr)
        raise SystemExit(1)
