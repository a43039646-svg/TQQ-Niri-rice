#!/usr/bin/env python3
"""A small GTK wallpaper preview picker controlled by the arrow keys."""
from __future__ import annotations

import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango


EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
APP_ID = "io.github.tqqniri.WallpaperPicker"
CHARACTERS = (
    ("ichika", "Ichika"),
    ("nino", "Nino"),
    ("miku", "Miku"),
    ("yotsuba", "Yotsuba"),
    ("itsuki", "Itsuki"),
)


def wallpaper_label(image: Path) -> str:
    stem = image.stem.casefold()
    names = [label for token, label in CHARACTERS if token in stem]
    if names:
        return " · ".join(names)
    return image.stem.replace("_", " ").replace("-", " ").title()


class WallpaperPicker(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application, images: list[Path], current: Path | None) -> None:
        super().__init__(application=application, title="Choose a wallpaper")
        self.images = images
        self.index = next((i for i, image in enumerate(images) if image == current), 0)
        self.set_decorated(False)
        self.set_resizable(True)
        self.set_modal(True)
        self.set_border_width(18)

        screen = Gdk.Screen.get_default()
        if screen:
            monitor = screen.get_monitor_at_point(0, 0)
            geometry = screen.get_monitor_geometry(monitor)
            self.preview_width = min(980, int(geometry.width * 0.72))
            self.preview_height = min(560, int(geometry.height * 0.62))
            self.set_default_size(min(1120, int(geometry.width * 0.84)), min(760, int(geometry.height * 0.84)))
        else:
            self.preview_width = 900
            self.preview_height = 520
            self.set_default_size(1000, 700)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            window { background-color: #171821; color: #f4f1f7; }
            label { color: #f4f1f7; }
            label.title { font-size: 18px; font-weight: 700; }
            button { background-image: none; background-color: #292b38; color: #f4f1f7;
                     border: 1px solid #49465b; border-radius: 14px; padding: 10px 16px; }
            button:hover { background-color: #393347; }
        """)
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(layout)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        layout.pack_start(header, False, False, 0)
        title = Gtk.Label(label="Choose a wallpaper")
        title.set_xalign(0)
        title.get_style_context().add_class("title")
        header.pack_start(title, True, True, 0)
        self.counter = Gtk.Label()
        header.pack_end(self.counter, False, False, 0)

        preview_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        layout.pack_start(preview_row, True, True, 0)

        previous = Gtk.Button(label="‹")
        previous.set_size_request(64, -1)
        previous.connect("clicked", lambda *_: self.step(-1))
        preview_row.pack_start(previous, False, False, 0)

        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        preview_row.pack_start(frame, True, True, 0)
        self.preview = Gtk.Image()
        self.preview.set_halign(Gtk.Align.CENTER)
        self.preview.set_valign(Gtk.Align.CENTER)
        frame.add(self.preview)

        following = Gtk.Button(label="›")
        following.set_size_request(64, -1)
        following.connect("clicked", lambda *_: self.step(1))
        preview_row.pack_end(following, False, False, 0)

        self.filename = Gtk.Label()
        self.filename.get_style_context().add_class("title")
        self.filename.set_ellipsize(Pango.EllipsizeMode.END)
        self.filename.set_xalign(0.5)
        layout.pack_start(self.filename, False, False, 0)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        layout.pack_end(footer, False, False, 0)
        hint = Gtk.Label(label="← / → Browse     Enter Apply     Esc Cancel")
        footer.pack_start(hint, True, True, 0)
        cancel = Gtk.Button(label="Cancel")
        cancel.connect("clicked", lambda *_: self.get_application().quit())
        footer.pack_end(cancel, False, False, 0)
        apply_button = Gtk.Button(label="Use wallpaper")
        apply_button.connect("clicked", lambda *_: self.apply())
        footer.pack_end(apply_button, False, False, 0)

        self.connect("key-press-event", self.on_key_press)
        self.show_all()
        self.refresh()

    def step(self, amount: int) -> None:
        self.index = (self.index + amount) % len(self.images)
        self.refresh()

    def refresh(self) -> None:
        image = self.images[self.index]
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                str(image), self.preview_width, self.preview_height, True
            )
            self.preview.set_from_pixbuf(pixbuf)
        except GLib.Error as error:
            print(f"Cannot preview {image}: {error}", file=sys.stderr)
            self.preview.clear()
        self.filename.set_text(wallpaper_label(image))
        self.counter.set_text(f"{self.index + 1} / {len(self.images)}")

    def on_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval in (Gdk.KEY_Left, Gdk.KEY_h):
            self.step(-1)
        elif event.keyval in (Gdk.KEY_Right, Gdk.KEY_l):
            self.step(1)
        elif event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.apply()
        elif event.keyval == Gdk.KEY_Escape:
            self.get_application().quit()
        else:
            return False
        return True

    def apply(self) -> None:
        print(self.images[self.index], flush=True)
        self.get_application().quit()


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} WALLPAPER_DIR CURRENT_WALLPAPER_FILE", file=sys.stderr)
        return 2
    wallpaper_dir = Path(sys.argv[1])
    state_file = Path(sys.argv[2])
    images = sorted(
        (path for path in wallpaper_dir.rglob("*") if path.is_file() and path.suffix.lower() in EXTENSIONS),
        key=lambda path: path.name.casefold(),
    )
    if not images:
        print(f"No wallpaper images found in {wallpaper_dir}", file=sys.stderr)
        return 1
    current = Path(state_file.read_text().strip()) if state_file.is_file() else None
    application = Gtk.Application(
        application_id=APP_ID,
        flags=Gio.ApplicationFlags.NON_UNIQUE,
    )

    def on_activate(app: Gtk.Application) -> None:
        window = WallpaperPicker(app, images, current)
        window.connect("destroy", lambda *_: app.quit())

    application.connect("activate", on_activate)
    return application.run([])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
