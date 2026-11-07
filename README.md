# TQQ Niri rice

A Niri desktop setup for Linux, themed around *The Quintessential Quintuplets*. The palette follows the active wallpaper: select an image once, and Matugen regenerates the colors used by Waybar, SwayNC, Rofi, and Fuzzel.

## Included

- **Island Waybar:** transparent bar with floating capsules for workspaces, clock, notifications, network, audio, battery, and tray.
- **SwayNC quick settings:** volume and brightness sliders, media controls, Do Not Disturb, a Wi-Fi picker, and notifications. The installer enables brightness only when it finds a backlight device.
- **Rofi app launcher:** four icon cards in one horizontal row; use Left/Right to browse and type to filter.
- **Fuzzel:** wallpaper picker and plain-text power menu. Reboot and power-off ask for confirmation.
- **Wallpaper switching:** `Super+W` opens the picker, `awww` applies the wallpaper with a transition when available, and `swaybg` is the fallback.
- **Wallpaper persistence:** the chosen image and palette are restored when Niri starts.
- **3D Fetch support:** an optional config for [areofyl/fetch](https://github.com/areofyl/fetch), with guarded shell autostart. Existing Fetch/Fastfetch startup is preserved.
- **Niri integration:** the installer backs up and patches the existing config instead of replacing the user's window rules and layout.

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

The installer needs an existing Niri config at `~/.config/niri/config.kdl` with a `binds {}` block. It adds the rice startup entries and keybindings while preserving the rest of that config.

To install dependencies explicitly:

```sh
./install.sh --install-deps
```

The installer backs up the existing Waybar, SwayNC, Fuzzel, Rofi, Matugen, Fetch, and Niri configs under `~/.local/state/tqq-niri-rice/backups/`. It copies the included wallpapers to `~/.local/share/tqq-niri-rice/wallpapers/`, installs helpers to `~/.local/bin/`, and chooses free Niri keybindings if the defaults are already used.

The regular installer does not change the display manager or install SDDM. The Niri config is backed up before patching; other config folders also get a dated backup before the rice files are copied over matching paths.

### Dependencies

Required programs: Niri, Waybar, SwayNC (`swaync` and `swaync-client`), Fuzzel, Rofi, Matugen, PipeWire/WirePlumber (`wpctl`), Python 3, and the standard process tools `pgrep`/`pkill`. For wallpaper display, install `awww` and its daemon or `swaybg`. NetworkManager (`nmcli`) enables the Wi-Fi picker; `notify-send` and `brightnessctl` are optional.

`scripts/check-dependencies` reports missing commands and package hints. `scripts/install-dependencies` has package recipes for Debian/Ubuntu, Arch, Fedora, and openSUSE. Package names and availability vary by release. The script installs Matugen through Cargo on releases without a package; Niri itself and optional awww transitions may need to be installed separately. The wallpaper switcher falls back to swaybg.

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

The installer first tries these keys, then chooses an unused alternative from its fallback list:

| Action | Preferred key |
| --- | --- |
| Choose wallpaper and update colors | `Super+W` |
| Open power menu | `Super+E` |
| Open Rofi app grid | `Mod+D` |

Waybar's audio capsule opens the SwayNC quick-settings panel. Right-clicking the notification capsule toggles Do Not Disturb.

## Config layout

- `config/waybar/` — Island layout and CSS that imports Matugen colors.
- `config/swaync/` — quick-settings widgets, Wi-Fi button, and matching CSS.
- `config/rofi/` — four-column icon launcher and dynamic theme import.
- `config/fuzzel/` — picker/menu UI and dynamic palette include.
- `config/matugen/` — dark wallpaper-derived templates for all four components.
- `config/fetch/` — 3D Fetch display settings.
- `scripts/` — wallpaper, power, Wi-Fi, dependency, Fetch autostart, SwayNC hardware detection, and Niri integration helpers.
- `wallpapers/` — the TQQ wallpaper collection installed to the rice data directory.
