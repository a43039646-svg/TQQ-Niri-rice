# TQQ Niri rice

A Niri desktop setup for Linux, themed around *The Quintessential Quintuplets*. Choose a wallpaper in the visual preview with the arrow keys; Matugen then regenerates the Waybar, SwayNC, and Fuzzel colors from that image, and updates 3D Fetch's label accent to the nearest terminal color.

## Included

- **Island Waybar:** transparent bar with floating capsules for workspaces, clock, notifications, network, audio, battery, and tray.
- **SwayNC quick settings:** volume and brightness sliders, media controls, Do Not Disturb, a Wi-Fi picker, and notifications. The installer enables brightness only when it finds a backlight device.
- **Wallpaper preview:** a centered floating GTK panel displays each wallpaper and its character names in English; use Left/Right to browse, Enter to apply, and Escape to cancel.
- **Fuzzel:** application launcher and plain-text power menu. Reboot and power-off ask for confirmation.
- **Wallpaper switching:** `Mod+B` (Win+B) opens the preview panel and updates the Matugen palette; `awww` applies the wallpaper with a transition when available, and `swaybg` is the fallback.
- **Wallpaper persistence:** the chosen image and palette are restored when Niri starts.
- **3D Fetch support:** an optional config for [areofyl/fetch](https://github.com/areofyl/fetch), with guarded shell autostart. Its label accent follows the wallpaper palette; existing Fetch/Fastfetch startup is preserved.
- **Niri config:** the installer backs up the existing config and preserves its settings and keybindings, adding the rice startup entries and only the Win+B wallpaper binding.

An optional SDDM theme is included under `config/sddm/TQQ`. It uses `imag1es.jpeg` as its background and follows the supplied reference with a large two-line clock, a dark glass-like panel, and a slow wallpaper zoom. To install and select it, run `./scripts/install-sddm-theme` or pass `--include-sddm` to the main installer. The SDDM theme installer backs up the previous theme and its own config snippet; it does not restart SDDM. It requires SDDM to already be installed.

## Install

The rice supports several Linux distributions. The installer checks its required commands and asks whether to install missing dependencies when run in a terminal. Package installation is also available explicitly with `--install-deps`; use `--skip-deps` to skip the prompt. The package manager will show its proposed changes and ask for confirmation. For distributions without a configured package recipe, install the listed dependencies manually.

Clone the repository and enter its directory:

```bash
git clone https://github.com/a43039646-svg/TQQ-Niri-rice.git
cd TQQ-Niri-rice
```

You can also use **Code → Download ZIP** on GitHub, extract the archive, and open a terminal in the extracted `TQQ-Niri-rice` folder.

Then run the installer:

```bash
./install.sh
```

The installer keeps the existing Niri config and keybindings, saves a dated backup, and adds the rice startup entries plus one Win+B wallpaper and palette binding.

To install dependencies explicitly:

```sh
./install.sh --install-deps
```

The installer backs up the existing Waybar, SwayNC, Fuzzel, Matugen, Fetch, and Niri configs under `~/.local/state/tqq-niri-rice/backups/`. It copies the included wallpapers to `${XDG_DATA_HOME:-~/.local/share}/tqq-niri-rice/wallpapers/` and installs helpers to `~/.local/bin/`. Existing Niri bindings are preserved; Win+B is reserved for wallpaper selection and palette generation.

The regular installer does not change the display manager or install SDDM. Existing Niri and component configs are backed up before the rice files are installed. If an older version of this rice replaced the Niri config, the installer tries to restore the newest original config backup first.

### Dependencies

Required programs: Niri, Waybar, SwayNC (`swaync` and `swaync-client`), Fuzzel, Matugen, PipeWire/WirePlumber (`wpctl`), Python 3 with GTK 3 PyGObject bindings, and the standard process tools `pgrep`/`pkill`. For wallpaper display, install `awww` and its daemon or `swaybg`. NetworkManager (`nmcli`) enables the Wi-Fi picker; `notify-send` and `brightnessctl` are optional.

`scripts/check-dependencies` reports missing commands and package hints. `scripts/install-dependencies` has package recipes for Debian/Ubuntu, Arch, Fedora, and openSUSE. Package names and availability vary by release. When Matugen is unavailable as a package, the installer uses its checksum-verified upstream x86_64 release; other architectures can build it with Rust 1.88 or newer. Niri itself and optional awww transitions may need to be installed separately. The wallpaper switcher falls back to swaybg.

### 3D Fetch

Fetch is optional and is not bundled. The installer checks for an existing Fetch/Fastfetch command in Bash or Zsh startup files. It does not add a duplicate; otherwise it prefers Fastfetch, then uses 3D Fetch with `fetch --box --shading-mode sextants`, and skips the shell entry if neither exists.

To build 3D Fetch from its upstream repository, follow its build instructions at [areofyl/fetch](https://github.com/areofyl/fetch). The matching config is in `config/fetch/config` and installs to `~/.config/fetch/config`.

For the upstream Make-based build on Debian, install its build tools, then clone and build it:

```bash
sudo apt install git build-essential
git clone https://github.com/areofyl/fetch.git
cd fetch
make
sudo make install
```

On other distributions, install the equivalent Git, compiler toolchain, and Make packages. The rice installer does not build or install Fetch automatically.

## Keybindings

The rice adds one wallpaper and palette shortcut to the existing Niri config and leaves the other bindings as they are:

| Action | Preferred key |
| --- | --- |
| Preview/apply wallpaper and update colors | `Mod+B` (Win+B) |

Waybar's audio capsule opens the SwayNC quick-settings panel. Right-clicking the notification capsule toggles Do Not Disturb.

## Config layout

- `config/waybar/` — Island layout and CSS that imports Matugen colors.
- `config/swaync/` — quick-settings widgets, Wi-Fi button, and matching CSS.
- `config/fuzzel/` — application and power-menu UI with a dynamic palette include.
- `config/matugen/` — dark wallpaper-derived templates for Waybar, SwayNC, and Fuzzel.
- `config/fetch/` — 3D Fetch display settings.
- `scripts/` — wallpaper preview, wallpaper application, power, Wi-Fi, dependency, Fetch autostart, SwayNC hardware detection, and Niri config helpers.
- `wallpapers/` — the TQQ wallpaper collection installed to the rice data directory.

Rofi is not used by this rice. If an existing `~/.config/rofi/` is present, the installer backs it up and removes it so the old Rofi setup is not left alongside Fuzzel.
