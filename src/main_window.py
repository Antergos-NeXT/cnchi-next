#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# main_window.py
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

""" Main Cnchi Window """

import os
import multiprocessing
import logging

import config
import desktop_info
import info
import misc.extra as misc

import pages.welcome
import pages.language
import pages.location
import pages.cache
import pages.check
import pages.desktop
import pages.features
import pages.keymap
import pages.timezone
import pages.user_info
import pages.slides
import pages.summary
import pages.mirrors
import pages.ask
import pages.automatic
import pages.alongside
import pages.advanced
import pages.zfs

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

try:
    _("")
except NameError as err:
    def _(message):
        return message

# Step definitions: (page_key, display_name, icon_name)
STEPS = [
    ("welcome", "Welcome", "go-home-symbolic"),
    ("language", "Language", "preferences-desktop-locale-symbolic"),
    ("check", "Check", "emblem-important-symbolic"),
    ("location", "Location", "mark-location-symbolic"),
    ("timezone", "Timezone", None),
    ("keymap", "Keyboard", "input-keyboard-symbolic"),
    ("desktop", "Desktop", "video-display-symbolic"),
    ("features", "Software", "applications-other-symbolic"),
    ("cache", "Preparation", "network-server-symbolic"),
    ("ask", "Install Type", "drive-harddisk-symbolic"),
    ("automatic", "Partitions", None),
    ("alongside", None, None),
    ("advanced", None, None),
    ("zfs", None, None),
    ("user_info", "Users", "avatar-default-symbolic"),
    ("summary", "Summary", "document-properties-symbolic"),
    ("slides", "Install", "system-run-symbolic"),
]

PAGE_ORDER = [
    "welcome", "language", "check", "location", "timezone",
    "keymap", "desktop", "features", "cache", "mirrors",
    "ask", "automatic", "alongside", "advanced", "zfs",
    "user_info", "summary", "slides",
]


class HeaderProxy:
    """ Proxy for page header operations in the new layout """
    def __init__(self, subtitle_label):
        self._label = subtitle_label

    def set_subtitle(self, text):
        self._label.set_text(text)
        self._label.set_visible(True)

    def set_show_close_button(self, visible):
        pass


class MainWindow(Gtk.ApplicationWindow):
    """ Cnchi main window """

    def __init__(self, app, cmd_line):
        Gtk.ApplicationWindow.__init__(self, title="Cnchi", application=app)

        self._main_window_width = 1200
        self._main_window_height = 715

        logging.info("Cnchi installer version %s", info.CNCHI_VERSION)

        self.settings = config.Settings()
        self.gui_dir = self.settings.get('ui')

        if not os.path.exists(self.gui_dir):
            cnchi_dir = os.path.join(os.path.dirname(__file__), '../')
            self.settings.set('cnchi', cnchi_dir)
            gui_dir = os.path.join(os.path.dirname(__file__), '../ui/')
            self.settings.set('ui', gui_dir)
            data_dir = os.path.join(os.path.dirname(__file__), '../data/')
            self.settings.set('data', data_dir)
            self.gui_dir = self.settings.get('ui')

        xz_cache = ["/var/cache/pacman/pkg"]
        if cmd_line.cache and cmd_line.cache not in xz_cache:
            xz_cache.append(cmd_line.cache)
        for xz_path in xz_cache:
            logging.debug("Cnchi will use '%s' as a source for cached xz packages", xz_path)
        self.settings.set('xz_cache', xz_cache)

        data_dir = self.settings.get('data')
        self.settings.set('hidden', cmd_line.hidden)
        self.settings.set('re_up', cmd_line.re_up)
        self.settings.set('a11y', cmd_line.a11y)

        if self.settings.get('hidden'):
            self.settings.set('desktops', desktop_info.DESKTOPS_DEV)
        elif self.settings.get('a11y'):
            self.settings.set('desktops', desktop_info.DESKTOPS_A11Y)
        else:
            self.settings.set('desktops', desktop_info.DESKTOPS)

        if cmd_line.environment:
            my_desktop = cmd_line.environment.lower()
            if my_desktop in desktop_info.DESKTOPS:
                self.settings.set('desktop', my_desktop)
                self.settings.set('desktop_ask', False)

        # Load main UI
        ui_builder = Gtk.Builder()
        path = os.path.join(self.gui_dir, "cnchi.ui")
        ui_builder.add_from_file(path)
        main = ui_builder.get_object("main")
        self.set_child(main)

        # UI elements
        self.sidebar = ui_builder.get_object("sidebar")
        self.logo_image = ui_builder.get_object("sidebar_logo")
        self.steps_list = ui_builder.get_object("steps_list")
        self.main_stack = ui_builder.get_object("main_stack")
        self.back_button = ui_builder.get_object("back_button")
        self.next_button = ui_builder.get_object("next_button")
        self.step_counter = ui_builder.get_object("step_counter")
        self.version_label = ui_builder.get_object("version_label")

        # Set logo
        logo_path = os.path.join(data_dir, "images", "antergos", "antergos-icon.png")
        if os.path.exists(logo_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 220, 220, True)
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            self.logo_image.set_from_paintable(texture)
            self.logo_image.set_hexpand(True)
            self.logo_image.set_halign(Gtk.Align.CENTER)

        # Set version
        self.version_label.set_text(f"v{info.CNCHI_VERSION}")

        # Progress bar for install
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_name('process_progressbar')
        self.progressbar.set_visible(False)
        progress_bar_box = ui_builder.get_object("progress_bar_box")
        progress_bar_box.append(self.progressbar)

        # Session params
        self.callback_queue = multiprocessing.JoinableQueue()
        if cmd_line.packagelist:
            self.settings.set('alternate_package_list', cmd_line.packagelist)

        self.params = dict()
        self.params['main_window'] = self
        self.params['gui_dir'] = self.gui_dir
        self.params['forward_button'] = self.next_button
        self.params['backwards_button'] = self.back_button
        self.params['callback_queue'] = self.callback_queue
        self.params['settings'] = self.settings
        self.params['main_progressbar'] = self.progressbar
        self.params['checks_are_optional'] = cmd_line.no_check
        self.params['no_tryit'] = cmd_line.no_tryit
        self.params['a11y'] = cmd_line.a11y

        # Header proxy for page subtitle updates
        self._page_subtitle = ui_builder.get_object("page_subtitle")
        self.params['header'] = HeaderProxy(self._page_subtitle)

        # Page storage
        self.pages = dict()
        self.page_order = []
        self.step_widgets = []
        self._current_page_idx = 0

        # Load first pages
        welcome_page = pages.welcome.Welcome(self.params)
        self._add_page("welcome", welcome_page)

        if os.path.exists('/home/antergos/.config/openbox'):
            lang_page = pages.language.Language(self.params)
            self._add_page("language", lang_page)
            self._main_window_width = 800
            self._main_window_height = 600

        # Build sidebar steps from loaded pages
        self._build_steps()
        self._switch_to_page(0)

        # Connect signals
        self.connect('close-request', self.on_exit_button_clicked)
        self.next_button.connect("clicked", self.on_forward_button_clicked)
        self.back_button.connect("clicked", self.on_backwards_button_clicked)

        # About button
        about_btn = ui_builder.get_object("about_button")
        about_btn.connect("clicked", self._on_about_clicked)

        # Keyboard shortcuts
        self._key_controller = Gtk.EventControllerKey.new()
        self._key_controller.connect("key-released", self.on_key_release)
        self.add_controller(self._key_controller)

        # Title
        nil, major, minor = info.CNCHI_VERSION.split('.')
        self.set_title(f"Cnchi {nil}.{major}.{minor}")

        # Set window icon
        icon_path = os.path.join(data_dir, "images", "antergos", "antergos-icon.png")
        if os.path.exists(icon_path):
            try:
                self.set_icon_name("cnchi")
            except Exception:
                pass

        # Set window geometry
        self.set_default_size(self._main_window_width, self._main_window_height)
        self.set_resizable(True)

        # Apply CSS
        style_provider = Gtk.CssProvider()
        style_css = os.path.join(data_dir, "css", "gtk-style.css")
        if os.path.exists(style_css):
            with open(style_css, 'rb') as css:
                style_provider.load_from_data(css.read())
            display = Gdk.Display.get_default()
            Gtk.StyleContext.add_provider_for_display(
                display, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        self.present()
        self.current_page.prepare('forwards')

        # Pre-load more pages
        self.pages["language"] = pages.language.Language(self.params)
        self.pages["check"] = pages.check.Check(self.params)
        self.set_focus(None)
        misc.gtk_refresh()

    def _build_steps(self):
        """ Create step indicator widgets in sidebar based on loaded pages """
        self.steps_list.remove_all()
        self.step_widgets = []

        for i, page_name in enumerate(self.page_order):
            display_name = None
            for step_name, step_display, _icon in STEPS:
                if step_name == page_name:
                    display_name = step_display
                    break
            if display_name is None:
                display_name = page_name.capitalize()

            row = Gtk.ListBoxRow()
            row.set_selectable(False)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_start(16)
            hbox.set_margin_end(16)
            hbox.set_margin_top(8)
            hbox.set_margin_bottom(8)

            indicator = Gtk.Label(label=str(i + 1))
            indicator.set_css_classes(["step-indicator"])
            indicator.set_size_request(28, 28)
            indicator.set_halign(Gtk.Align.CENTER)
            indicator.set_valign(Gtk.Align.CENTER)

            label = Gtk.Label(label=display_name)
            label.set_halign(Gtk.Align.START)
            label.set_hexpand(True)
            label.set_css_classes(["step-label"])
            label.set_xalign(0)

            hbox.append(indicator)
            hbox.append(label)
            row.set_child(hbox)
            self.steps_list.append(row)
            self.step_widgets.append((indicator, label, row, page_name))

    def _add_page(self, name, page_instance):
        """ Add a page to the stack and page tracking """
        if name in self.pages:
            return
        self.pages[name] = page_instance
        self.page_order.append(name)
        self.main_stack.add_named(page_instance, name)

    def _switch_to_page(self, idx):
        """ Switch to page at given index with animation """
        if idx < 0 or idx >= len(self.page_order):
            return

        page_name = self.page_order[idx]
        page = self.pages.get(page_name)
        if page is None:
            return

        # Set transition direction
        if idx > self._current_page_idx:
            self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        elif idx < self._current_page_idx:
            self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        else:
            self.main_stack.set_transition_type(Gtk.StackTransitionType.NONE)

        self.main_stack.set_visible_child(page)
        self._current_page_idx = idx
        self.current_page = page

        # Update step indicators
        self._update_steps()

        # Update navigation
        self.back_button.set_visible(idx > 0)
        total = len(self.page_order)
        self.step_counter.set_text(f"Step {idx + 1} of {total}")

        # Update next button label
        if idx == total - 1:
            self.next_button.set_label("Install")
        elif page_name in ("ask",):
            self.next_button.set_label("Next")
        else:
            self.next_button.set_label("Next")

        # Update progress
        if total > 1:
            self.progressbar.set_fraction((idx + 1) / total)

        page.prepare('forwards' if idx > 0 else 'initial')

    def _update_steps(self):
        """ Update step indicator visuals """
        for i, (indicator, label, _row, _pname) in enumerate(self.step_widgets):
            classes_ind = ["step-indicator"]
            classes_lbl = ["step-label"]
            if i == self._current_page_idx:
                classes_ind.append("active")
                classes_lbl.append("active")
            elif i < self._current_page_idx:
                classes_ind.append("completed")
                # Replace number with checkmark
                indicator.set_label("✓")
                classes_lbl.append("completed")
            else:
                pass  # default dimmed style
            indicator.set_css_classes(classes_ind)
            label.set_css_classes(classes_lbl)

    def _find_page_index(self, name):
        """ Find index of page by name """
        try:
            return self.page_order.index(name)
        except ValueError:
            return -1

    def load_pages(self):
        """ Preload all installer pages """
        if "location" not in self.pages:
            self._add_page("location", pages.location.Location(self.params))

        if "timezone" not in self.pages:
            self._add_page("timezone", pages.timezone.Timezone(self.params))

        if self.settings.get('desktop_ask'):
            self._add_page("keymap", pages.keymap.Keymap(self.params))
            self._add_page("desktop", pages.desktop.DesktopAsk(self.params))
            self._add_page("features", pages.features.Features(self.params))
        else:
            self._add_page("keymap", pages.keymap.Keymap(self.params, next_page='features'))
            self._add_page("features", pages.features.Features(self.params, prev_page='keymap'))

        self._add_page("cache", pages.cache.Cache(self.params))
        self._add_page("mirrors", pages.mirrors.Mirrors(self.params))
        self._add_page("ask", pages.ask.InstallationAsk(self.params))
        self._add_page("automatic", pages.automatic.InstallationAutomatic(self.params))

        if self.settings.get("enable_alongside"):
            self._add_page("alongside", pages.alongside.InstallationAlongside(self.params))

        self._add_page("advanced", pages.advanced.InstallationAdvanced(self.params))
        self._add_page("zfs", pages.zfs.InstallationZFS(self.params))
        self._add_page("user_info", pages.user_info.UserInfo(self.params))
        self._add_page("summary", pages.summary.Summary(self.params))
        self._add_page("slides", pages.slides.Slides(self.params))

        # Rebuild sidebar with all steps
        self._build_steps()
        self._update_steps()

        diff = 2
        if os.path.exists('/home/antergos/.config/openbox'):
            diff = 3
        num_pages = len(self.pages) - diff
        if num_pages > 0:
            self.progressbar_step = 1.0 / num_pages

    def on_forward_button_clicked(self, _button):
        """ Handle forward/next button """
        self._go_forward()

    def on_backwards_button_clicked(self, _button):
        """ Handle back button """
        self._go_backward()

    def _on_about_clicked(self, _button):
        """ Show About Cnchi dialog """
        dialog = Gtk.AlertDialog()
        dialog.set_message(f"Cnchi v{info.CNCHI_VERSION}")
        dialog.set_detail(
            "Antergos NeXT Installer\n\n"
            "GTK4 Calamares-inspired installer\n"
            "Originally based on EndeavourOS-ISO\n\n"
            "Copyright © 2026 Antergos NeXT")
        dialog.set_buttons(["_Close"])
        dialog.set_modal(True)
        dialog.choose(self, None, lambda *a: None)

    def _go_forward(self):
        """ Move to next page """
        idx = self._current_page_idx + 1
        if idx >= len(self.page_order):
            return
        self.current_page.store_values()
        self._switch_to_page(idx)

    def _go_backward(self):
        """ Move to previous page """
        idx = self._current_page_idx - 1
        if idx < 0:
            return
        self.current_page.go_back()
        self._switch_to_page(idx)

    def on_key_release(self, controller, keyval, keycode, state):
        """ Handle keyboard shortcuts """
        if keyval == Gdk.KEY_Right or keyval == Gdk.KEY_KP_Right:
            self._go_forward()
        elif keyval == Gdk.KEY_Left or keyval == Gdk.KEY_KP_Left:
            self._go_backward()
        elif keyval == Gdk.KEY_Escape:
            self.on_exit_button_clicked()

    def on_exit_button_clicked(self, *args):
        """ Exit installer """
        self.destroy()

    def set_focus(self, widget):
        """ Set keyboard focus """
        if widget:
            widget.grab_focus()
