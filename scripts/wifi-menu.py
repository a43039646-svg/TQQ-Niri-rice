#!/usr/bin/env python3
"""Pick and connect to a NetworkManager Wi-Fi network using Fuzzel."""
from __future__ import annotations

import shutil
import subprocess
import sys


def split_nmcli(line: str) -> list[str]:
    fields: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    fields.append("".join(current))
    return fields


def notify(message: str) -> None:
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "TQQ Wi-Fi", message], check=False)
    else:
        print(message, file=sys.stderr)


if not shutil.which("nmcli"):
    notify("Install NetworkManager to use the Wi-Fi picker.")
    raise SystemExit(1)

try:
    result = subprocess.run(
        ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes"],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
except (OSError, subprocess.SubprocessError) as error:
    notify(f"Couldn't scan Wi-Fi networks: {error}")
    raise SystemExit(1)

entries: list[tuple[str, str, str]] = []
seen: set[str] = set()
for line in result.stdout.splitlines():
    fields = split_nmcli(line)
    if len(fields) < 3:
        continue
    ssid, signal, security = (field.strip() for field in fields[:3])
    if not ssid:
        continue
    label = f"{ssid}  ·  {signal or '?'}%  ·  {security or 'Open'}"
    if label not in seen:
        entries.append((label, ssid, security))
        seen.add(label)

if not entries:
    notify("No visible Wi-Fi networks were found.")
    raise SystemExit(0)

try:
    picked = subprocess.run(
        ["fuzzel", "--dmenu", "--prompt=Wi-Fi > "],
        input="\n".join(label for label, _, _ in entries) + "\n",
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
except OSError as error:
    notify(f"Couldn't open Fuzzel: {error}")
    raise SystemExit(1)
if not picked:
    raise SystemExit(0)

chosen = next(((ssid, security) for label, ssid, security in entries if label == picked), None)
if chosen is None:
    raise SystemExit(1)
ssid, security = chosen
command = ["nmcli", "device", "wifi", "connect", ssid]
if security:
    try:
        password = subprocess.run(
            ["fuzzel", "--dmenu", "--password", "--prompt=Wi-Fi password > "],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.rstrip("\n")
    except OSError as error:
        notify(f"Couldn't open the password prompt: {error}")
        raise SystemExit(1)
    if not password:
        raise SystemExit(0)
    command += ["password", password]

try:
    connected = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
except (OSError, subprocess.SubprocessError) as error:
    notify(f"Connection failed: {error}")
    raise SystemExit(1)
if connected.returncode == 0:
    notify(f"Connected to {ssid}.")
else:
    notify(connected.stderr.strip() or f"Couldn't connect to {ssid}.")
    raise SystemExit(1)
