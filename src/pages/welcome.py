#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# welcome.py
#
# Copyright © 2026 Antergos NeXT NeXT NeXT
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

""" Welcome screen """

import os
import logging
import multiprocessing
import sys

import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

from gi.repository import Gdk
from gi.repository import Gtk

import misc.extra as misc
from pages.gtkbasebox import GtkBaseBox
import quotes

# When testing, no _() is available
try:
    _("")
except NameError as err:
    def _(message):
        return message


_KONAMI = [
    Gdk.KEY_Up, Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Down,
    Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Left, Gdk.KEY_Right,
    Gdk.KEY_b, Gdk.KEY_a,
]


class Welcome(GtkBaseBox):
    """ Welcome screen class """

    def __init__(self, params, prev_page=None, next_page="language"):
        super().__init__(self, params, "welcome", prev_page, next_page)

        data_dir = self.settings.get('data')
        welcome_dir = os.path.join(data_dir, "images", "welcome")

        self._konami_idx = 0
        self._konami_timer = None

        self.main_window = params['main_window']

        self.labels = {'welcome': self.gui.get_object("welcome_label"),
                       'tryit': self.gui.get_object("tryit_welcome_label"),
                       'installit': self.gui.get_object("installit_welcome_label"),
                       'loading': self.gui.get_object("loading_label"),
                       'quote': self.gui.get_object("quote_label")}

        self.buttons = {'tryit': self.gui.get_object("tryit_button"),
                        # 'cli': self.gui.get_object("cli_button"),
                        'graph': self.gui.get_object("graph_button")}

        for key in self.buttons:
            btn = self.buttons[key]
            btn.set_name(key + "_btn")

        self.images = {'tryit': self.gui.get_object("tryit_image"),
                       # 'cli': self.gui.get_object("cli_image"),
                       'graph': self.gui.get_object("graph_image")}

        self.filenames = {
            'tryit': {
                'path': os.path.join(welcome_dir, "try-it.svg"),
                'width': 211,
                'height': 185},
            'graph': {
                'path': os.path.join(welcome_dir, "install-it.svg"),
                'width': 211,
                'height': 185}}

        # a11y
        self.labels['tryit'].set_mnemonic_widget(self.buttons['tryit'])
        self.labels['installit'].set_mnemonic_widget(self.buttons['graph'])

        for key in self.images:
            image = self.filenames[key]
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                image['path'],
                image['width'],
                image['height'])
            self.images[key].set_from_pixbuf(pixbuf)

        # Locale fallback warning
        self._locale_warning = None
        from cnchi import CnchiInit
        if CnchiInit._locale_fallback:
            self._locale_warning = Gtk.Label()
            self._locale_warning.set_property('wrap', True)
            self._locale_warning.set_property('justify', 'center')
            self._locale_warning.set_property('margin_top', 10)
            self._locale_warning.set_property('margin_bottom', 10)
            self._locale_warning.set_name('locale-warning-label')
            self.gui.get_object('welcome').pack_start(
                self._locale_warning, False, False, 0)
            self.gui.get_object('welcome').reorder_child(
                self._locale_warning, 1)

    def translate_ui(self):
        """ Translates all ui elements """
        if not self.no_tryit:
            txt = _("Use Antergos NeXT without making any changes to your system.")
        else:
            txt = ""
        self.labels['tryit'].set_markup(txt)
        self.labels['tryit'].set_name('tryit_label')

        txt = _("Create a permanent place for Antergos NeXT on your system.")
        self.labels['installit'].set_markup(txt)
        self.labels['installit'].set_name('installit_label')

        txt = _("Try It")
        self.buttons['tryit'].set_label(txt)

        # txt = _("CLI Installer")
        # self.buttons['cli'].set_label(txt)

        txt = _("Install It")
        self.buttons['graph'].set_label(txt)

        txt = _("Welcome to Antergos NeXT!")
        self.header.set_subtitle(txt)

    def quit_cnchi(self):
        """ Quits installer """
        misc.remove_temp_files(self.settings.get('temp'))
        for proc in multiprocessing.active_children():
            proc.terminate()
        logging.shutdown()
        sys.exit(0)

    def on_tryit_button_clicked(self, _widget, _data=None):
        """ Try live CD, quits installer """
        self.quit_cnchi()

    def on_graph_button_clicked(self, _widget, _data=None):
        """ User wants to install """
        self.show_loading_message()
        # Tell timezone process to start searching now
        self.settings.set('timezone_start', True)
        # Simulate a forward button click
        self.forward_button.clicked()

    def show_loading_message(self, do_show=True):
        """ Shows a message so the user knows Cnchi is loading pages
            only when running from liveCD """
        if do_show:
            txt = _("Loading, please wait...")
        else:
            txt = ""
        self.labels['loading'].set_markup(txt)
        self.labels['loading'].queue_draw()
        misc.gtk_refresh()

    def store_values(self):
        """ Store changes (none in this page) """
        self.forward_button.show()
        return True

    def _on_key_press(self, _widget, event):
        """ Track Konami code sequence """
        if not self.settings.get('re_up'):
            return False
        if event.keyval == _KONAMI[self._konami_idx]:
            self._konami_idx += 1
            if self._konami_idx >= len(_KONAMI):
                self._konami_idx = 0
                self._trigger_konami()
                return True
        else:
            self._konami_idx = 0
        return False

    def _trigger_konami(self):
        """ Konami code entered: cycle through all quotes """
        import gi
        gi.require_version('GLib', '2.0')
        from gi.repository import GLib

        def cycle_quotes():
            self.labels['quote'].set_markup(
                '<span size="small" style="italic">"{}"</span>'.format(
                    quotes.get_random_quote()))
            return True

        self._konami_timer = GLib.timeout_add(800, cycle_quotes)

    def prepare(self, direction):
        """ Prepare page before showing it """
        self.translate_ui()

        if self._locale_warning:
            txt = _(
                "The live environment's locales does not have your language. "
                "The fallback is currently in English. "
                "If you cannot navigate and do not know English, "
                "I suggest Google Lens.")
            self._locale_warning.set_markup(
                '<span foreground="#FFA500">⚠ {}</span>'.format(txt))
            self._locale_warning.show()

        self.show_all()
        self.forward_button.hide()

        if self.settings.get('re_up'):
            self.labels['quote'].set_markup(
                '<span size="small" style="italic">"{}"</span>'.format(
                    quotes.get_random_quote()))
            self.labels['quote'].show()
        else:
            self.labels['quote'].hide()

        self._konami_idx = 0
        self.main_window.connect('key-press-event', self._on_key_press)

        # a11y Set install option as default if ENTER is pressed
        self.buttons['graph'].set_can_default(True)
        self.main_window.set_default(self.buttons['graph'])

        if self.no_tryit:
            self.buttons['tryit'].set_sensitive(False)
        if direction == "backwards":
            self.show_loading_message(do_show=False)
