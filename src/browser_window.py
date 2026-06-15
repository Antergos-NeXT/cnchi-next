#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# webview.py
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

""" Web View """

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, GLib, WebKit

class BrowserWindow(Gtk.Window):
    """ Shows a browser window showing passed url """
    def __init__(self, _title, width=800, height=600):
        Gtk.Window.__init__(self)

        self.set_size_request(width, height)

        self.set_resizable(False)
        scrolled_window = Gtk.ScrolledWindow()
        self.set_child(scrolled_window)

        self.connect('close-request', self.on_destroy)

        settings = WebKit.Settings.new(
            enable_javascript=True,
            enable_webgl=False,
        )
        self.webview = WebKit.WebView.new_with_settings(settings)

        self.webview.connect('decide-policy', self.decide_policy_cb)
        self.webview.connect('load-changed', self.load_changed_cb)

        scrolled_window.set_child(self.webview)

    def on_destroy(self, _event, _data):
        """ Destroys window """
        self.destroy()

    @staticmethod
    def decide_policy_cb(_webview, decision, _decision_type):
        """ Allows all (security flaw, but we do not care when installing) """
        decision.allow()
        return True

    def load_changed_cb(self, _webview, _load_event):
        pass

    def load_url(self, url):
        """ Load url """
        GLib.idle_add(self.webview.load_uri, url)
