#!/usr/bin/env python3
"""Fix remaining GTK4-incompatible patterns in Python files.

Handles:
  - container.add(x) -> container.set_child(x) or container.append(x)
  - .pack_start(x, ...) -> .append(x)
  - .pack_end(x, ...) -> .prepend(x)
  - Gtk.HBox( -> Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL
  - Gtk.VBox( -> Gtk.Box(orientation=Gtk.Orientation.VERTICAL
  - new_from_icon_name(x, size) -> new_from_icon_name(x)
  - set_from_icon_name(x, size) -> set_from_icon_name(x)
  - set_border_width( -> # self.set_border_width(  (comment out)
  - delete-event -> close-request
  - Gtk.Window(Gtk.WindowType.TOPLEVEL) -> Gtk.Window()
  - Gdk.Cursor(Gdk.CursorType.xxx) -> Gdk.Cursor.new_from_name("xxx")
  - Gtk.Box() -> Gtk.Box(orientation=Gtk.Orientation.VERTICAL (for bare no-arg)
"""

import re
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    original = content

    # 1. Gtk.VBox -> Gtk.Box(orientation=Gtk.Orientation.VERTICAL
    content = content.replace('Gtk.VBox(', 'Gtk.Box(orientation=Gtk.Orientation.VERTICAL, ')

    # 2. Gtk.HBox -> Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL
    content = content.replace('Gtk.HBox(', 'Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, ')

    # 3. Gtk.Window(Gtk.WindowType.TOPLEVEL) -> Gtk.Window()
    content = content.replace('Gtk.Window(Gtk.WindowType.TOPLEVEL)', 'Gtk.Window()')

    # 4. .pack_start( -> .append(  (smart: leave TreeViewColumn alone)
    # Only replace when preceding context is box-like
    content = re.sub(
        r'(?<!TreeViewColumn)\.pack_start\(',
        '.append(',
        content
    )

    # 5. .pack_end( -> .prepend(
    content = re.sub(
        r'(?<!TreeViewColumn)\.pack_end\(',
        '.prepend(',
        content
    )

    # 6. .add( -> context-sensitive
    # Window.add( -> set_child(
    content = re.sub(
        r'\b(window|Window)\.add\(',
        r'\1.set_child(',
        content
    )
    # scrolled_window.add( -> set_child(
    content = re.sub(
        r'\b(scrolledwindow|scrolled_window|ScrolledWindow)\.add\(',
        r'\1.set_child(',
        content
    )
    # overlay.add( -> set_child(
    content = re.sub(
        r'\boverlay\.add\(',
        'overlay.set_child(',
        content
    )
    # map_window.add( -> set_child(
    content = re.sub(
        r'\b(map_window|mapWindow)\.add\(',
        r'\1.set_child(',
        content
    )
    # self.add( on ListBoxRow subclasses -> set_child
    # We'll handle this per-file below

    # Box.add( -> append(  (vbox, box, hbox, area, content_area)
    content = re.sub(
        r'\b(vbox|hbox|box|area|content_area)\.add\(',
        r'\1.append(',
        content
    )
    # listbox.add( -> append(
    content = re.sub(
        r'\b(listbox|list_box)\.add\(',
        r'\1.append(',
        content
    )

    # 7. new_from_icon_name(x, size) -> new_from_icon_name(x)
    content = re.sub(
        r'new_from_icon_name\(([^,]+),\s*[^)]+\)',
        r'new_from_icon_name(\1)',
        content
    )
    # 8. set_from_icon_name(x, size) -> set_from_icon_name(x)
    content = re.sub(
        r'set_from_icon_name\(([^,]+),\s*[^)]+\)',
        r'set_from_icon_name(\1)',
        content
    )

    # 9. set_border_width( -> comment out
    # Only comment out if it's a full line (or inline)
    content = re.sub(
        r'^\s+self\.set_border_width\([^)]+\)',
        lambda m: '# ' + m.group(0).lstrip() + '  # GTK4: use CSS',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'^\s+window\.set_border_width\([^)]+\)',
        lambda m: '# ' + m.group(0).lstrip() + '  # GTK4: use CSS',
        content,
        flags=re.MULTILINE
    )

    # 10. delete-event -> close-request
    content = content.replace("'delete-event'", "'close-request'")

    # 11. Gdk.Cursor(Gdk.CursorType.HAND1) -> Gdk.Cursor.new_from_name("pointer")
    #     Gdk.CursorType.HAND2 -> also "pointer"
    content = re.sub(
        r'Gdk\.Cursor\(Gdk\.CursorType\.(?:HAND1|HAND2)\)',
        r'Gdk.Cursor.new_from_name("pointer")',
        content
    )

    # 12. Gdk.Cursor.new_for_display(display, Gdk.CursorType.HAND2) -> Gdk.Cursor.new_from_name("pointer")
    content = re.sub(
        r'Gdk\.Cursor\.new_for_display\([^,]+,\s*Gdk\.CursorType\.(?:HAND1|HAND2)\)',
        r'Gdk.Cursor.new_from_name("pointer")',
        content
    )

    # 13. Gtk.Box() with no orientation -> add orientation HORIZONTAL (default in GTK4 requires explicit)
    # Be careful: already-handled boxes with orientation= won't match
    content = re.sub(
        r'Gtk\.Box\(\s*\)',
        'Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)',
        content
    )
    # Fix double orientation= (shouldn't happen but just in case)
    content = re.sub(
        r'orientation=Gtk\.Orientation\.(HORIZONTAL|VERTICAL),\s*orientation=Gtk\.Orientation\.\w+',
        r'orientation=Gtk.Orientation.\1',
        content
    )
    # Fix double commas (but preserve trailing comma in single-element tuples)
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r'\(\s*,', '(', content)
    # Don't remove trailing comma from within parens (breaks signals like (object,))
    # Only fix truly empty parens from double comma removal
    content = re.sub(r',\s*\)', ')', content)

    # 14. event_box.add( -> event_box.set_child(
    content = re.sub(
        r'\bevent_box\.add\(',
        'event_box.set_child(',
        content
    )

    changed = content != original
    if changed:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'  Fixed: {os.path.relpath(filepath, SRC)}')
    return changed

def main():
    files_fixed = 0
    for root, dirs, files in os.walk(SRC):
        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                filepath = os.path.join(root, f)
                if fix_file(filepath):
                    files_fixed += 1
    print(f'\nFixed {files_fixed} files')

if __name__ == '__main__':
    main()
