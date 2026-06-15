#!/bin/bash
#cow_spacesize=1G
sudo mount -o remount,size=1G /run/archiso/cowspace
sudo pacman -Syy --noconfirm
sudo pacman -S python
sudo pacman -S webkit2gtk
sudo pacman -S iso-codes gptfdisk python python-bugsnag \
python-cairo python-chardet python-dbus python-defusedxml \
python-feedparser python-gobject python-idna \
python-libnacl python-mako python-parted \
python-requests upower python-urllib3 pyalpm


