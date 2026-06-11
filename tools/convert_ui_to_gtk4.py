#!/usr/bin/env python3
"""Convert GTK3 .ui files to GTK4 using lxml."""

import os, sys, re
from lxml import etree

UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'ui')

REMOVE_PROPS = {
    'shadow_type', 'border_width', 'window_position',
    'stock', 'use_action_appearance', 'no_show_all',
    'draw_indicator', 'type_hint', 'skip_taskbar_hint',
    'skip_pager_hint', 'urgency_hint',
    'always_show_image', 'has_resize_grip', 'message_type',
    'invisible_char', 'xalign', 'yalign',
    'primary_icon_activatable', 'secondary_icon_activatable',
    'layout_style', 'use_stock', 'buttons', 'icon', 'pixbuf',
}
# Properties to remove only from specific widget classes
REMOVE_PROPS_BY_CLASS = {
    'GtkButton': {'image'},
}
RENAME_PROPS = {
    'margin_left': 'margin-start',
    'margin_right': 'margin-end',
    'margin-left': 'margin-start',
    'margin-right': 'margin-end',
}
REMOVE_CLASSES = {'GtkEventBox'}
RENAME_CLASSES = {
    'GtkRadioButton': 'GtkCheckButton',
    'GtkDialog': 'GtkWindow',
    'GtkMessageDialog': 'GtkWindow',
    'GtkButtonBox': 'GtkBox',
}
# Properties to remove from specific widget classes
REMOVE_PROPS_BY_CLASS = {
    'GtkButton': {'image'},
}


def convert_file(path):
    with open(path) as f:
        original = f.read()

    content = original

    # 1. Pre-process with regex
    content = re.sub(
        r'requires lib="gtk\+" version="3\.\d+"',
        'requires lib="gtk" version="4.0"', content)
    content = re.sub(r'<signal\s+[^>]*/>', '', content)
    content = re.sub(r'<relation>[^<]*<[^>]*>[^<]*</relation>', '', content)
    content = re.sub(r'<relation\s+[^>]*/>', '', content)
    content = re.sub(r'<action-widgets>.*?</action-widgets>', '', content, flags=re.DOTALL)

    if content == original:
        changed_str = False
    else:
        changed_str = True
        # Write pre-processed for lxml to parse
        with open(path, 'w') as f:
            f.write(content)

    # 2. Process with lxml
    try:
        tree = etree.parse(path)
    except Exception as e:
        print(f'  PARSE ERROR: {os.path.relpath(path, UI_DIR)} - {e}')
        if changed_str:
            # Restore original
            with open(path, 'w') as f:
                f.write(original)
        return False

    root = tree.getroot()
    changed_xml = False

    def process_element(elem):
        nonlocal changed_xml
        cls = elem.get('class', '') or ''

        # Remove widgets that don't exist in GTK4 (GtkEventBox, etc.)
        if cls in REMOVE_CLASSES:
            parent = elem.getparent()
            if parent is not None and parent.tag == 'child':
                grandparent = parent.getparent()
                if grandparent is not None:
                    idx = list(grandparent).index(parent)
                    grandparent.remove(parent)
                    # Promote the eventbox's inner children into grandparent
                    for i, inner_child in enumerate(list(elem.findall('child'))):
                        grandparent.insert(idx + i, inner_child)
                    changed_xml = True
            elif parent is not None:
                idx = list(parent).index(elem)
                parent.remove(elem)
                for i, child in enumerate(list(elem.findall('child'))):
                    parent.insert(idx + i, child)
                changed_xml = True
            return

        # Rename widget classes that changed in GTK4
        if cls in RENAME_CLASSES:
            elem.set('class', RENAME_CLASSES[cls])
            changed_xml = True

        # Remove/rename properties
        for prop in list(elem.findall('property')):
            pname = prop.get('name', '')
            if pname in REMOVE_PROPS:
                elem.remove(prop)
                changed_xml = True
            elif pname in RENAME_PROPS:
                prop.set('name', RENAME_PROPS[pname])
                changed_xml = True

        # Remove class-specific properties
        if cls in REMOVE_PROPS_BY_CLASS:
            for prop in list(elem.findall('property')):
                if prop.get('name') in REMOVE_PROPS_BY_CLASS[cls]:
                    elem.remove(prop)
                    changed_xml = True

        # Fix attributes on the element
        for attr in list(elem.attrib):
            if attr in REMOVE_PROPS or attr == 'no_show_all':
                del elem.attrib[attr]
            elif attr == 'internal-child':
                # GTK4 removed internal children (vbox in GtkDialog, etc.)
                del elem.attrib[attr]
                changed_xml = True
            elif attr in RENAME_PROPS:
                elem.attrib[RENAME_PROPS[attr]] = elem.attrib[attr]
                del elem.attrib[attr]
                changed_xml = True

        # Remove icon-size from GtkImage
        if 'GtkImage' in cls:
            for prop in list(elem.findall('property')):
                if prop.get('name') == 'icon-size':
                    elem.remove(prop)
                    changed_xml = True

    for elem in root.iter():
        process_element(elem)

    # Convert <packing> inside <child>: move packing props to child widget properties
    for child_elem in root.iter('child'):
        packing = child_elem.find('packing')
        if packing is not None:
            child_obj = child_elem.find('object')
            if child_obj is not None:
                for prop in list(packing.findall('property')):
                    pname = prop.get('name', '')
                    if pname == 'position':
                        continue
                    if pname == 'expand':
                        new_prop = etree.SubElement(child_obj, 'property')
                        new_prop.set('name', 'hexpand')
                        new_prop.text = prop.text
                        new_prop.tail = prop.tail
                        new_prop2 = etree.SubElement(child_obj, 'property')
                        new_prop2.set('name', 'vexpand')
                        new_prop2.text = prop.text
                        new_prop2.tail = prop.tail
                        changed_xml = True
                    elif pname == 'fill':
                        new_prop = etree.SubElement(child_obj, 'property')
                        new_prop.set('name', 'halign')
                        new_prop.text = 'fill'
                        new_prop.tail = prop.tail
                        new_prop2 = etree.SubElement(child_obj, 'property')
                        new_prop2.set('name', 'valign')
                        new_prop2.text = 'fill'
                        new_prop2.tail = prop.tail
                        changed_xml = True
                    elif pname == 'pack-type':
                        pass  # No direct GTK4 equivalent
            child_elem.remove(packing)
            changed_xml = True

    if changed_str or changed_xml:
        result = etree.tostring(
            tree, encoding='unicode', pretty_print=True,
            xml_declaration=False)
        result = result.replace(
            "<?xml version='1.0' encoding='UTF-8'?>",
            '<?xml version="1.0" encoding="UTF-8"?>')
        result = result.replace(
            '<?xml version="1.0" encoding="ascii"?>',
            '<?xml version="1.0" encoding="UTF-8"?>')
        result = '<?xml version="1.0" encoding="UTF-8"?>\n' + result
        result = re.sub(r'\n{3,}', '\n\n', result)
        with open(path, 'w') as f:
            f.write(result)
        return True

    # Restore original if no changes
    if changed_str and not changed_xml:
        with open(path, 'w') as f:
            f.write(original)
        return False

    return changed_xml or changed_str


def main():
    count = 0
    for root_dir, dirs, files in os.walk(UI_DIR):
        for fname in sorted(files):
            if not fname.endswith('.ui'):
                continue
            path = os.path.join(root_dir, fname)
            rel = os.path.relpath(path, UI_DIR)
            if convert_file(path):
                print(f'  Converted: {rel}')
                count += 1
            else:
                print(f'  OK:        {rel}')
    print(f'\nConverted {count} files')


if __name__ == '__main__':
    main()
