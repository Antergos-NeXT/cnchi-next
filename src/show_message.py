#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# show_message.py
#
# Copyright © 2026 Antergos NeXT
#
# This file is part of Cnchi.
#
# Cnchi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Cnchi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# The following additional terms are in effect as per Section 7 of the license:
#
# The preservation of all legal notices and author attributions in
# the material or in the Appropriate Legal Notices displayed
# by works containing it is required.
#
# You should have received a copy of the GNU General Public License
# along with Cnchi; If not, see <http://www.gnu.org/licenses/>.

""" Helper functions to show Gtk message dialogs """

import sys
import os

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from misc import extra as misc

try:
    _("")
except NameError as err:
    def _(msg):
        return msg


def _make_alert(title, message, buttons=None):
    alert = Gtk.AlertDialog()
    alert.set_message(title)
    alert.set_detail(str(message))
    if buttons:
        alert.set_buttons(buttons)
    return alert


def fatal_error(parent, my_message):
    path = "/var/tmp/cnchi/.setup-running"
    if os.path.exists(path):
        with misc.raised_privileges():
            os.remove(path)
    error(parent, my_message)
    sys.exit(1)


def error(parent, my_message):
    if not isinstance(parent, Gtk.Window):
        parent = None
    alert = _make_alert(
        _("Antergos NeXT Installer - Error"),
        my_message,
        [_("_Close")])
    alert.choose(parent, None, lambda *a: None)


def warning(parent, my_message):
    if not isinstance(parent, Gtk.Window):
        parent = None
    alert = _make_alert(
        _("Antergos NeXT Installer - Warning"),
        my_message,
        [_("_Close")])
    alert.choose(parent, None, lambda *a: None)


def message(parent, my_message):
    if not isinstance(parent, Gtk.Window):
        parent = None
    alert = _make_alert(
        _("Antergos NeXT Installer - Information"),
        my_message,
        [_("_Close")])
    alert.choose(parent, None, lambda *a: None)


def question(parent, my_message):
    if not isinstance(parent, Gtk.Window):
        parent = None
    alert = _make_alert(
        _("Antergos NeXT Installer - Confirmation"),
        my_message,
        [_("_No"), _("_Yes")])
    alert.set_default_button(1)
    alert.set_cancel_button(0)
    response = None
    loop = GLib.MainLoop()
    def on_response(dialog, result):
        nonlocal response
        try:
            idx = dialog.choose_finish(result)
        except GLib.Error:
            idx = -1
        if idx == 1:
            response = Gtk.ResponseType.YES
        elif idx == 0:
            response = Gtk.ResponseType.NO
        else:
            response = Gtk.ResponseType.NO
        loop.quit()
    alert.choose(parent, None, on_response)
    loop.run()
    return response
