""" CHANNEL 666 - secret easter egg mode for Cnchi """

import os
import random
import logging
import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, Gdk, GLib

_ACTIVE = False
_MPV_PROC = None
_GLITCH_TIMER = None
_WINDOW = None
_ORIG_TITLE = "Cnchi"
_CSS_PROVIDER = None
_GLITCH_COUNT = 0

_GLITCH_CSS = """
window {
    background-color: #0a0000;
}
window label, window button, window text {
    color: #8b0000;
    text-shadow: 0 0 8px #8b0000, 0 0 16px #ff0000;
}
"""

def _zalgo_title():
    zalgo_chars = [
        '\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305',
        '\u0306', '\u0307', '\u0308', '\u0309', '\u030a', '\u030b',
        '\u030c', '\u030d', '\u030e', '\u030f', '\u0310', '\u0311',
        '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317',
        '\u0318', '\u0319', '\u031a', '\u031b', '\u031c', '\u031d',
        '\u031e', '\u031f', '\u0320', '\u0321', '\u0322', '\u0323',
        '\u0324', '\u0325', '\u0326', '\u0327', '\u0328', '\u0329',
        '\u032a', '\u032b', '\u032c', '\u032d', '\u032e', '\u032f',
        '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335',
        '\u0336', '\u0337', '\u0338', '\u0339', '\u033a', '\u033b',
        '\u033c', '\u033d', '\u033e', '\u033f',
    ]
    parts = ["R", " ", "U", " ", "N"]
    result = []
    for p in parts:
        if p.strip():
            result.append(p + ''.join(random.choice(zalgo_chars) for _ in range(random.randint(3, 8))))
        else:
            result.append(p)
    return ''.join(result)

def _glitch_tick():
    global _GLITCH_COUNT
    if not _ACTIVE or not _WINDOW:
        return False
    _GLITCH_COUNT += 1
    try:
        # Title glitches every few ticks
        if _GLITCH_COUNT % random.randint(2, 5) == 0:
            _WINDOW.set_title(_zalgo_title())

        # Subtle opacity dip occasionally
        if random.random() < 0.15:
            _WINDOW.set_opacity(random.uniform(0.85, 0.95))
        elif random.random() < 0.1:
            _WINDOW.set_opacity(1.0)

        # Tiny position jitter
        if random.random() < 0.08:
            x, y = _WINDOW.get_position()
            _WINDOW.set_position(x + random.randint(-2, 2), y + random.randint(-1, 1))
    except Exception:
        pass
    return True

def _find_audio():
    paths = [
        "/usr/share/cnchi-memes/i-feel-fantastic.opus",
        "/usr/share/cnchi-memes/i-feel-fantastic.mp3",
        "/usr/share/cnchi-memes/666.opus",
        "/usr/share/cnchi-memes/666.mp3",
        os.path.join(os.path.dirname(__file__), "../../data/audio/i-feel-fantastic.opus"),
        os.path.join(os.path.dirname(__file__), "../../data/audio/666.opus"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def _play_audio():
    global _MPV_PROC
    if _MPV_PROC and _MPV_PROC.poll() is None:
        return
    audio = _find_audio()
    if not audio:
        logging.warning("CHANNEL 666: no audio file found")
        return
    try:
        _MPV_PROC = subprocess.Popen(
            ["mpv", "--no-video", "--loop", "--volume=70", audio],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        logging.warning("CHANNEL 666: mpv not found")

def _stop_audio():
    global _MPV_PROC
    if _MPV_PROC and _MPV_PROC.poll() is None:
        _MPV_PROC.terminate()
        try:
            _MPV_PROC.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _MPV_PROC.kill()
        _MPV_PROC = None

def activate(window):
    global _ACTIVE, _GLITCH_TIMER, _WINDOW, _ORIG_TITLE, _CSS_PROVIDER, _GLITCH_COUNT
    if _ACTIVE:
        return
    _ACTIVE = True
    _GLITCH_COUNT = 0
    _WINDOW = window
    _ORIG_TITLE = window.get_title()

    _CSS_PROVIDER = Gtk.CssProvider()
    _CSS_PROVIDER.load_from_string(_GLITCH_CSS)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        _CSS_PROVIDER,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    _GLITCH_TIMER = GLib.timeout_add(100, _glitch_tick)
    _play_audio()

    window.set_title("R̸̨̢ ̛U̶̕͝ ̡N̸̕")
    logging.info("CHANNEL 666 ACTIVATED")

def deactivate(_window=None):
    global _ACTIVE, _GLITCH_TIMER, _WINDOW, _CSS_PROVIDER
    if not _ACTIVE:
        return
    _ACTIVE = False
    if _GLITCH_TIMER:
        GLib.source_remove(_GLITCH_TIMER)
        _GLITCH_TIMER = None

    if _WINDOW:
        _WINDOW.set_opacity(1.0)
        _WINDOW.set_title("Cnchi")

    _stop_audio()

    if _CSS_PROVIDER:
        try:
            display = Gdk.Display.get_default()
            Gtk.StyleContext.remove_provider_for_display(display, _CSS_PROVIDER)
        except Exception:
            pass
        _CSS_PROVIDER = None

    _WINDOW = None
    logging.info("CHANNEL 666 DEACTIVATED")

def is_active():
    return _ACTIVE
