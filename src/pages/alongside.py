#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# alongside.py
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

""" Alongside installation module """

import os
import logging
import subprocess
import tempfile

import show_message as show
import bootinfo

import parted3.fs_module as fs

from misc.run_cmd import call
from installation import install

from pages.gtkbasebox import GtkBaseBox

import misc.extra as misc
import misc.gtkwidgets as gtkwidgets

# When testing, no _() is available
try:
    _("")
except NameError as err:
    def _(message):
        return message

DEST_DIR = "/install"

def get_partition_size_info(partition_path, human=False):
    """ Gets partition used and available space using df command """

    min_size = "0"
    part_size = "0"

    already_mounted = False

    with open("/proc/mounts") as mounts:
        if partition_path in mounts.read():
            already_mounted = True

    tmp_dir = ""

    try:
        cmd = []
        if not already_mounted:
            tmp_dir = tempfile.mkdtemp()
            cmd = ['/usr/bin/mount', partition_path, tmp_dir]
            subprocess.check_output(cmd)
        if human:
            cmd = ['/usr/bin/df', '-h', partition_path]
        else:
            cmd = ['/usr/bin/df', partition_path]
        df_out = subprocess.check_output(cmd).decode()
        if not already_mounted:
            subprocess.check_output(['/usr/bin/umount', '-l', tmp_dir])
    except subprocess.CalledProcessError as err:
        logging.error("Error running command %s: %s", err.cmd, err.output)
        return

    if os.path.exists(tmp_dir):
        os.rmdir(tmp_dir)

    if df_out:
        df_out = df_out.split('\n')
        df_out = df_out[1].split()
        if human:
            part_size = df_out[1]
            min_size = df_out[2]
        else:
            part_size = float(df_out[1])
            min_size = float(df_out[2])

    return min_size, part_size

class InstallationAlongside(GtkBaseBox):
    """ Performs an automatic installation next to a previous installed OS """

    # Leave at least 6.5GB for Antergos NeXT when shrinking
    MIN_ROOT_SIZE = 8000

    def __init__(self, params, prev_page="installation_ask", next_page="user_info"):
        super().__init__(self, params, "alongside", prev_page, next_page)

        self.label = self.gui.get_object('label_info')

        self.choose_partition_label = self.gui.get_object(
            'choose_partition_label')
        self.choose_partition_combo = self.gui.get_object(
            'choose_partition_combo')

        self.oses = bootinfo.get_os_dict()
        # print(self.oses)
        self.resize_widget = None

    @staticmethod
    def get_disk_from_partition(partition_path):
        """ Resolve the parent disk device from a partition path """
        cmd = ["lsblk", "-n", "-o", "PKNAME", partition_path]
        try:
            pkname = subprocess.check_output(cmd).decode().strip()
            if pkname:
                return "/dev/" + pkname
        except subprocess.CalledProcessError:
            pass
        # Fallback: strip trailing digits
        dev = partition_path.rstrip("0123456789")
        if dev.endswith("p"):
            dev = dev[:-1]
        return dev

    @staticmethod
    def get_partition_number(partition_path):
        """ Get partition number from a device path """
        cmd = ["lsblk", "-n", "-o", "MINOR", partition_path]
        try:
            minor = subprocess.check_output(cmd).decode().strip()
            # The partition number is usually (minor - 1) for the main disk
            # More reliably, read from /sys
            real_path = os.path.realpath(partition_path)
            partname = os.path.basename(real_path)
            # Strip non-digit prefix to get number
            num = partname
            while num and not num[0].isdigit():
                num = num[1:]
            if num:
                return int(num)
        except (subprocess.CalledProcessError, ValueError):
            pass
        return 1

    @staticmethod
    def get_new_device(device_to_shrink):
        """ Get next available partition device on the same disk """
        disk = InstallationAlongside.get_disk_from_partition(device_to_shrink)
        part_num = InstallationAlongside.get_partition_number(device_to_shrink)
        # Check if the original path uses 'p' before number (nvme/mmcblk)
        sep = "p" if "p{0}".format(part_num) in device_to_shrink else ""
        new_number = part_num + 1
        new_device = "{0}{1}{2}".format(disk, sep, new_number)
        while misc.partition_exists(new_device):
            new_number += 1
            new_device = "{0}{1}{2}".format(disk, sep, new_number)
        return new_device

    def set_resize_widget(self, device_to_shrink):
        """ Get resize widget ready """
        new_device = self.get_new_device(device_to_shrink)

        if new_device is None:
            # No device is available
            logging.error("There are no primary partitions available")
            return

        txt = "Will shrink device {0} and create new device {1}".format(
            device_to_shrink, new_device)
        logging.debug(txt)

        (min_size, part_size) = get_partition_size_info(device_to_shrink)
        max_size = part_size - (InstallationAlongside.MIN_ROOT_SIZE * 1000.0)
        if max_size < 0:
            # Full Antergos NeXT does not fit but maybe base fits... ask user.
            txt = _("Cnchi recommends at least 6.5GB free to install Antergos NeXT. \n\n"
                    "New partition {0} resulting of shrinking {1} will not have enough\n"
                    "free space for a full installation.\n"
                    "You can still install Antergos NeXT, but be carefull on which DE you\n"
                    "choose as it might not fit in.\n\n"
                    "Install at your own risk!\n\n")
            txt = txt.format(new_device, device_to_shrink)
            show.warning(self.get_main_window(), txt)
            max_size = part_size

        # print(min_size, max_size, part_size)

        if self.resize_widget:
            self.resize_widget.set_property('part_size', int(part_size))
            self.resize_widget.set_property('min_size', int(min_size))
            self.resize_widget.set_property('max_size', int(max_size))
        else:
            self.resize_widget = gtkwidgets.ResizeWidget(
                part_size, min_size, max_size)
            main_box = self.gui.get_object('alongside')
            main_box.append(self.resize_widget)
            self.resize_widget.set_vexpand(True)
            self.resize_widget.set_margin_top(5)
            self.resize_widget.set_margin_bottom(5)

        self.resize_widget.set_part_title(
            'existing', self.oses[device_to_shrink], device_to_shrink)
        icon_file = self.get_distributor_icon_file(self.oses[device_to_shrink])
        self.resize_widget.set_part_icon('existing', icon_file=icon_file)

        self.resize_widget.set_part_title('new', 'New Antergos NeXT', new_device)
        icon_file = self.get_distributor_icon_file('Antergos NeXT')
        self.resize_widget.set_part_icon('new', icon_file=icon_file)

        self.resize_widget.set_pref_size(max_size)

    def get_distributor_icon_file(self, os_name):
        """ Gets an icon for the installed distribution """
        os_name = os_name.lower()

        # No numix icon for Antergos NeXT, use our own.
        if "antergos" in os_name:
            icons_path = os.path.join(self.settings.get('data'), "icons/48x48")
            icon_file = os.path.join(
                icons_path, "distributor-logo-antergos.png")
            return icon_file

        icon_names = [
            "lfs", "magiea", "manjaro", "mint", "archlinux", "chakra",
            "debian", "deepin", "fedora", "gentoo", "opensuse", "siduction",
            "kubuntu", "lubuntu", "ubuntu", "windows"]
        prefix = "distributor-logo-"
        sufix = ".svg"

        icons_path = os.path.join(self.settings.get('data'), "icons/scalable")
        default = os.path.join(icons_path, "distributor-logo.svg")

        for name in icon_names:
            if name in os_name:
                return os.path.join(icons_path, prefix + name + sufix)

        return default

    def translate_ui(self):
        """ Translates all ui elements """
        txt = _("Choose the new size of your installation")
        txt = '<span size="large">{0}</span>'.format(txt)
        self.label.set_markup(txt)

        txt = _("Choose the partition that you want to shrink:")
        self.choose_partition_label.set_markup(txt)

        self.header.set_subtitle(_("Antergos NeXT Alongside Installation"))

    def choose_partition_changed(self, combobox):
        """ The user has chosen a device from the combobox """
        txt = combobox.get_active_text()
        device = txt.split("(")[1][:-1]
        # print(device)
        self.set_resize_widget(device)

    def prepare(self, direction):
        """ Prepare our dialog to show/hide/activate/deactivate what's necessary """
        self.translate_ui()
        self.fill_choose_partition_combo()

    def fill_choose_partition_combo(self):
        """ Fill widget with partitions info """
        self.choose_partition_combo.remove_all()

        devices = []

        for device in sorted(self.oses.keys()):
            # if "Swap" not in self.oses[device]:
            if "windows" in self.oses[device].lower():
                devices.append(device)

        if len(devices) > 1:
            new_device_found = False
            for device in sorted(devices):
                if self.get_new_device(device):
                    new_device_found = True
                    line = "{0} ({1})".format(self.oses[device], device)
                    self.choose_partition_combo.append_text(line)
            misc.select_first_combobox_item(self.choose_partition_combo)
            if not new_device_found:
                txt = _("Can't find any spare partition number.\n"
                        "Alongside installation can't continue.")
                self.choose_partition_label.hide()
                self.choose_partition_combo.hide()
                self.label.set_markup(txt)
                show.error(self.get_main_window(), txt)
        elif len(devices) == 1:
            self.set_resize_widget(devices[0])
            self.choose_partition_label.hide()
            self.choose_partition_combo.hide()
        else:
            logging.warning("Can't find any installed OS")

    def store_values(self):
        """ Store user choices """
        self.start_installation()
        return True

    # #################################################################################

    def start_installation(self):
        """ Alongside method shrinks selected partition
        and creates root and swap partition in the available space """

        (existing_os, existing_device) = self.resize_widget.get_part_title_and_subtitle(
            'existing')
        new_os, new_device = self.resize_widget.get_part_title_and_subtitle('new')

        logging.debug("existing: %s %s", existing_os, existing_device)
        logging.debug("new: %s %s", new_os, new_device)

        partition_path = existing_device
        new_size_mb = self.resize_widget.get_new_part_size()
        disk_path = self.get_disk_from_partition(partition_path)
        part_num = self.get_partition_number(partition_path)
        fs_type = fs.get_type(partition_path)

        if not fs_type:
            txt = _("Cannot detect filesystem type on {0}").format(partition_path)
            logging.error(txt)
            show.error(self.get_main_window(), txt)
            return

        is_uefi = os.path.exists("/sys/firmware/efi")

        # Detect GPT
        is_gpt = False
        cmd = ["parted", "-s", disk_path, "print"]
        try:
            output = subprocess.check_output(cmd).decode()
            if "gpt" in output.split("\n")[0].lower():
                is_gpt = True
        except subprocess.CalledProcessError:
            pass

        # Get partition start position (in MiB)
        part_start = 1
        try:
            cmd = ["parted", "-s", disk_path, "unit", "MiB", "print"]
            output = subprocess.check_output(cmd).decode()
            for line in output.split("\n"):
                if line.strip().startswith(str(part_num)):
                    cols = line.split()
                    if len(cols) >= 2:
                        part_start = float(cols[1].rstrip("MiB"))
                        break
        except (subprocess.CalledProcessError, ValueError):
            pass

        # Step 1: Shrink the filesystem
        logging.debug("Shrinking filesystem %s on %s to %d MiB", fs_type, partition_path, new_size_mb)
        self.events.add('info', _("Shrinking filesystem on {0}...").format(partition_path))
        if not fs.resize(partition_path, fs_type, new_size_mb):
            txt = _("Could not shrink filesystem on {0}").format(partition_path)
            logging.error(txt)
            show.error(self.get_main_window(), txt)
            return

        # Step 2: Shrink the partition
        new_end = part_start + new_size_mb
        logging.debug("Shrinking partition %s to %d MiB (end at %d)", partition_path, new_size_mb, new_end)
        self.events.add('info', _("Resizing partition..."))
        cmd = ["parted", "-s", "-a", "min", disk_path, "unit", "MiB", "resizepart",
               str(part_num), str(new_end)]
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            txt = _("Could not shrink partition: {0}").format(err.output.decode())
            logging.error(txt)
            show.error(self.get_main_window(), txt)
            return

        subprocess.check_output(["udevadm", "settle"])

        # Step 3: Calculate swap size
        mem_total = subprocess.check_output(["grep", "MemTotal", "/proc/meminfo"]).decode()
        mem_total = int(mem_total.split()[1])
        mem = mem_total / 1024

        if mem < 2048:
            swap_part_size = 2 * mem
        elif 2048 <= mem < 8192:
            swap_part_size = mem
        elif 8192 <= mem < 65536:
            swap_part_size = mem / 2
        else:
            swap_part_size = 4096

        swap_part_size = int(swap_part_size)

        # Get total disk size to calculate remaining free space
        disk_end = 0
        try:
            cmd = ["parted", "-s", disk_path, "unit", "MiB", "print"]
            output = subprocess.check_output(cmd).decode()
            for line in output.split("\n"):
                if "Disk /" in line and "MiB" in line:
                    disk_end = float(line.split()[-1].rstrip("MiB"))
                    break
        except (subprocess.CalledProcessError, ValueError):
            disk_end = 0

        free_space_mb = disk_end - new_end

        if free_space_mb < InstallationAlongside.MIN_ROOT_SIZE:
            txt = _("Not enough free space for Antergos NeXT installation (need {0} MiB)").format(
                InstallationAlongside.MIN_ROOT_SIZE)
            logging.error(txt)
            show.error(self.get_main_window(), txt)
            return

        no_swap = False
        if free_space_mb < InstallationAlongside.MIN_ROOT_SIZE + swap_part_size:
            if mem < 2048:
                txt = _("Cannot create new swap partition. Not enough free space.")
                logging.error(txt)
                show.error(self.get_main_window(), txt)
                return
            no_swap = True

        mount_devices = {}
        fs_devices = {}

        current_start = new_end

        def parted_create(disk_path, fs_label, fs_type, start, end, is_gpt, part_num):
            """ Create a partition with parted, handling MBR vs GPT """
            if is_gpt:
                cmd = ["parted", "-s", "-a", "min", disk_path, "unit", "MiB",
                       "mkpart", fs_label, fs_type, str(start), str(end)]
            else:
                ptype = "logical" if part_num >= 4 else "primary"
                cmd = ["parted", "-s", "-a", "min", disk_path, "unit", "MiB",
                       "mkpart", ptype, fs_type, str(start), str(end)]
            return cmd

        if no_swap:
            root_end = current_start + free_space_mb
            cmd = parted_create(disk_path, "AntergosRoot", "ext4",
                                current_start, root_end, is_gpt, part_num)
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                txt = _("Could not create root partition: {0}").format(err.output.decode())
                logging.error(txt)
                show.error(self.get_main_window(), txt)
                return
            subprocess.check_output(["udevadm", "settle"])
            root_device = self.get_new_device(partition_path)
            failed, msg = fs.create_fs(root_device, 'ext4', 'AntergosRoot')
            if failed:
                logging.error("Could not create filesystem on %s: %s", root_device, msg)
            mount_devices["/"] = root_device
            fs_devices[root_device] = "ext4"
        else:
            swap_end = current_start + swap_part_size
            cmd = parted_create(disk_path, "AntergosSwap", "linux-swap",
                                current_start, swap_end, is_gpt, part_num)
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                txt = _("Could not create swap partition: {0}").format(err.output.decode())
                logging.error(txt)
                show.error(self.get_main_window(), txt)
                return
            subprocess.check_output(["udevadm", "settle"])
            swap_device = self.get_new_device(partition_path)
            failed, msg = fs.create_fs(swap_device, 'swap', 'AntergosSwap')
            if failed:
                logging.error("Could not create swap on %s: %s", swap_device, msg)
            mount_devices["swap"] = swap_device
            fs_devices[swap_device] = "swap"

            current_start = swap_end
            root_end = current_start + (free_space_mb - swap_part_size)
            cmd = parted_create(disk_path, "AntergosRoot", "ext4",
                                current_start, root_end, is_gpt, part_num)
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                txt = _("Could not create root partition: {0}").format(err.output.decode())
                logging.error(txt)
                show.error(self.get_main_window(), txt)
                return
            subprocess.check_output(["udevadm", "settle"])
            root_device = self.get_new_device(partition_path)
            failed, msg = fs.create_fs(root_device, 'ext4', 'AntergosRoot')
            if failed:
                logging.error("Could not create filesystem on %s: %s", root_device, msg)
            mount_devices["/"] = root_device
            fs_devices[root_device] = "ext4"

        # Step 4: Set bootloader
        self.settings.set('bootloader_install', True)
        self.settings.set('bootloader', "grub2")
        self.settings.set('bootloader_device', disk_path)

        if is_gpt and is_uefi:
            esp_device = None
            try:
                cmd = ["parted", "-s", disk_path, "print"]
                output = subprocess.check_output(cmd).decode()
                lines = output.split("\n")
                in_table = False
                for line in lines:
                    if line.startswith("Number"):
                        in_table = True
                        continue
                    if in_table and line.strip():
                        cols = line.split()
                        if len(cols) >= 7:
                            flags = cols[-1].lower() if len(cols) > 6 else ""
                            if "esp" in flags:
                                part_no = cols[0]
                                esp_device = "{0}{1}".format(
                                    disk_path, part_no
                                ) if not disk_path[-1].isdigit() else "{0}p{1}".format(
                                    disk_path, part_no)
                                break
            except subprocess.CalledProcessError:
                pass

            if not esp_device:
                for esp_candidate in [
                    "{0}1".format(disk_path),
                    "{0}p1".format(disk_path)
                ]:
                    if os.path.exists(esp_candidate):
                        info = fs.get_info(esp_candidate)
                        if info and info.get("TYPE") == "vfat":
                            esp_device = esp_candidate
                            break

            if esp_device:
                mount_devices["/boot/efi"] = esp_device
                fs_devices[esp_device] = "vfat"

        msg = "Antergos NeXT will install the bootloader {0} in device {1}"
        msg = msg.format(self.settings.get('bootloader'), disk_path)
        logging.info(msg)

        # Step 5: Start installation
        ssd = {disk_path: fs.is_ssd(disk_path)}

        self.installation = install.Installation(
            self.settings,
            self.callback_queue,
            None,
            None,
            mount_devices,
            fs_devices,
            ssd)

        self.installation.run()
