# Cnchi ![version](https://img.shields.io/badge/version-0.16.52--next-blue.svg) ![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg) [![Build Packages](https://github.com/Antergos-NeXT/antergos-pkgs/actions/workflows/build.yml/badge.svg)](https://github.com/Antergos-NeXT/antergos-pkgs/actions/workflows/build.yml)

**Graphical installer for Arch Linux** — revived and maintained by **Antergos NeXT**.

Forked from the original Antergos Cnchi, patched for modern Python (3.14+), with updated package lists and support for 10 desktop environments.

| Branch | Status |
|--------|--------|
| `0.16.x` | Active — stable release |
| `master` | Legacy upstream |

## What's different in this fork

- **Python 3.14 compat** — `crypt` → `passlib`, `locale.getdefaultlocale()` fixed, `unittest.mock` replaces standalone `mock`
- **WebKit2 4.1** — updated from deprecated 4.0
- **Updated packages.xml** — all 522 packages resolve against current Arch repos, 94 dead packages replaced
- **Rebranded** — URLs, package names, and references updated to Antergos NeXT
- **Multi-DE** — KDE Plasma (default), GNOME, XFCE, Cinnamon, Budgie, Deepin, LXQt, MATE, Enlightenment, Openbox, i3

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
