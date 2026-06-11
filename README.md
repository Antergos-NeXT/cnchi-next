# Cnchi ![version](https://img.shields.io/badge/version-0.16.52--next-blue.svg) ![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg) [![Build Packages](https://github.com/Antergos-NeXT/antergos-pkgs/actions/workflows/build.yml/badge.svg)](https://github.com/Antergos-NeXT/antergos-pkgs/actions/workflows/build.yml)

**Graphical installer for Arch Linux** — revived and maintained by **Antergos NeXT**.

Forked from the original Antergos Cnchi, patched for modern Python (3.14+), with updated package lists and support for 10 desktop environments.

| Branch | Status |
|--------|--------|
| `0.16.x` | Active — stable GTK3 release |
| `cnchi-dev` | Development — **GTK4 redesign**, experimental features |
| `master` | Legacy upstream |

## What's different in this fork

- **Python 3.14 compat** — `crypt` → `passlib`, `locale.getdefaultlocale()` fixed, `unittest.mock` replaces standalone `mock`
- **WebKit2 4.1** — updated from deprecated 4.0
- **Updated packages.xml** — all 522 packages resolve against current Arch repos, 94 dead packages replaced
- **Rebranded** — URLs, package names, and references updated to Antergos NeXT
- **Multi-DE** — KDE Plasma (default), GNOME, XFCE, Cinnamon, Budgie, Deepin, LXQt, MATE, Enlightenment, Openbox, i3

## Cnchi-Development (GTK4 branch)

The `cnchi-dev` branch is a **ground-up UI redesign** porting Cnchi from GTK3 to GTK4 with a Calamares-inspired layout.

### Key differences from `0.16.x` (GTK3 stable)

- **GTK4** — ported from GTK3, uses `gi.require_version('Gtk', '4.0')`, `Gtk.AlertDialog`, `Gdk.Texture`, etc.
- **Calamares-inspired layout** — sidebar with animated step indicators, horizontal split layout
- **Animated transitions** — `GtkStack` with `SLIDE_LEFT`/`SLIDE_RIGHT` transitions between pages
- **Modern dark theme** — custom CSS with gradients, glow effects, pulse animations
- **Navigation arrows** — keyboard Left/Right arrows for back/next
- **WebKit 6.0** — `webkitgtk-6.0` replaces `webkit2gtk-4.1`
- **Quotes by default** — welcome screen quotes no longer need `--re-up` flag
- **About dialog** — sidebar About button with `Gtk.AlertDialog`

### Dependencies (GTK4)

- **gtk4**, python, python-cairo, python-gobject, python-dbus
- python-requests, python-chardet, python-feedparser, python-idna
- python-mako, python-geoip2, python-maxminddb, python-passlib
- pyalpm, python-pyparted, parted, dosfstools, mtools, ntfs-3g
- upower, gocryptfs, iso-codes, **webkitgtk-6.0**

## Usage

```sh
sudo -E cnchi.py
```

### Options

| Flag | Description |
|------|-------------|
| `-a`, `--a11y` | Enable accessibility features by default |
| `-c`, `--cache` | Use pre-downloaded xz packages when possible |
| `-d`, `--debug` | Set log level to debug |
| `-e`, `--environment` | Set DE to install (see `src/desktop_info.py`) |
| `-f`, `--force` | Run even if another instance is detected |
| `-n`, `--no-check` | Skip checks in check screen |
| `-p`, `--packagelist` | Use a local XML package list instead of default |
| `-t`, `--no-tryit` | Disable 'try it' option on first screen |
| `-v`, `--verbose` | Show log messages to stdout  |
| `-V`, `--version` | Show version and quit |
| `-z`, `--hidden` | Show development options |
| `--re-up` | Enable Class of '09 quotes on welcome screen (enabled by default in cnchi-dev) |

## Reporting bugs

Open an issue at [github.com/Antergos-NeXT/Cnchi](https://github.com/Antergos-NeXT/Cnchi/issues) with:

- `/var/log/cnchi/cnchi.log`
- `/var/log/cnchi/cnchi-alpm.log`
- `/var/log/cnchi/postinstall.log`
- `/var/log/cnchi/pacman.log`

## Building

Packaged via [antergos-pkgs](https://github.com/Antergos-NeXT/antergos-pkgs). The PKGBUILD pulls from this repo's `0.16.x` branch.

## Dependencies

- gtk3, python, python-cairo, python-gobject, python-dbus
- python-requests, python-chardet, python-feedparser, python-idna
- python-mako, python-geoip2, python-maxminddb, python-passlib
- pyalpm, python-pyparted, parted, dosfstools, mtools, ntfs-3g
- upower, gocryptfs, iso-codes, webkit2gtk-4.1

## License

[GPL-3.0](COPYING)
