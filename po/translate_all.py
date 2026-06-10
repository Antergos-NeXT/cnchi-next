"""Translate major language .po files using Google Translate"""
import os, re, json, time
import requests

PO_DIR = '/home/xalatath/Antergos-NeXT-ISO/Cnchi/po'

LANGS = [
    'de', 'fr', 'es', 'it', 'pt', 'pt_BR', 'ru', 'ja', 'ko',
    'zh_CN', 'zh_TW', 'ar', 'nl', 'sv', 'nb', 'da', 'fi',
    'cs', 'sk', 'hu', 'ro', 'bg', 'el', 'tr', 'uk', 'hi', 'id', 'vi',
]

GOOGLE_LANG = {
    'de': 'de', 'fr': 'fr', 'es': 'es', 'it': 'it', 'pt': 'pt',
    'pt_BR': 'pt', 'ru': 'ru', 'ja': 'ja', 'ko': 'ko',
    'zh_CN': 'zh-CN', 'zh_TW': 'zh-TW', 'ar': 'ar', 'nl': 'nl',
    'sv': 'sv', 'nb': 'no', 'da': 'da', 'fi': 'fi',
    'cs': 'cs', 'sk': 'sk', 'hu': 'hu', 'ro': 'ro',
    'bg': 'bg', 'el': 'el', 'tr': 'tr', 'uk': 'uk',
    'hi': 'hi', 'id': 'id', 'vi': 'vi',
}

DELAY = 0.5

def unescape(s):
    r = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            c = s[i+1]
            if c == 'n':      r.append('\n'); i += 2
            elif c == 't':    r.append('\t'); i += 2
            elif c == '\\':   r.append('\\'); i += 2
            elif c == '"':    r.append('"'); i += 2
            elif c == 'r':    r.append('\r'); i += 2
            else:             r.append(s[i]); i += 1
        else:
            r.append(s[i]); i += 1
    return ''.join(r)

def escape_po(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    return s

def google_trans(text, target, retries=3):
    url = 'https://translate.googleapis.com/translate_a/single'
    params = {'client': 'gtx', 'sl': 'en', 'tl': target, 'dt': 't', 'q': text}
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params,
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            r.raise_for_status()
            result = json.loads(r.text)
            parts = []
            for segment in result[0]:
                if isinstance(segment, list) and len(segment) > 0 and segment[0]:
                    parts.append(segment[0])
            return ''.join(parts)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                raise

def get_text_from_msgid(msgid_lines):
    """Extract plain text from collected msgid lines"""
    raw = ''
    for line in msgid_lines:
        line = line.rstrip('\n')
        if line.startswith('msgid "') and line != 'msgid ""':
            raw += line.split('"', 1)[1].rsplit('"', 1)[0]
        elif line.startswith('"') and line.endswith('"'):
            raw += line[1:-1]
    return unescape(raw)

for lang in LANGS:
    po_path = os.path.join(PO_DIR, f'{lang}.po')
    if not os.path.exists(po_path):
        print(f"{lang}: no file")
        continue

    glang = GOOGLE_LANG.get(lang, lang)
    print(f"\n{lang}: reading...")

    with open(po_path, 'r') as f:
        lines = f.readlines()

    # Collect entries with empty msgstr
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#~') or line.startswith('#') or line == 'msgid ""\n':
            i += 1
            continue
        if line.startswith('msgid "') and line != 'msgid ""\n':
            msgid_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith('"') and not lines[i].startswith('"Project-'):
                msgid_lines.append(lines[i])
                i += 1
            # Now i points to msgstr line (or something else)
            if i < len(lines) and lines[i].strip() == 'msgstr ""':
                text = get_text_from_msgid(msgid_lines)
                if text:
                    entries.append((i, text, msgid_lines))
                i += 1
                while i < len(lines) and lines[i].startswith('"'):
                    i += 1
                continue
            # Skip to next entry
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                i += 1
            continue
        i += 1

    if not entries:
        print(f"  already fully translated")
        continue

    print(f"  {len(entries)} to translate")
    done = 0

    for line_idx, text, msgid_lines in entries:
        # Check if original text ends with newline
        ends_with_nl = text.endswith('\n')
        try:
            result = google_trans(text, glang)
            if result:
                if ends_with_nl and not result.endswith('\n'):
                    result += '\n'
                safe = escape_po(result)
                lines[line_idx] = f'msgstr "{safe}"\n'
                done += 1
            time.sleep(DELAY)
        except Exception as e:
            print(f"  FAIL: {text[:40]}... -> {e}")
            time.sleep(10)

    with open(po_path, 'w') as f:
        f.writelines(lines)

    # Compile
    ret = os.system(f'msgfmt "{po_path}" -o /dev/null 2>&1')
    errors = os.popen(f'msgfmt "{po_path}" -o /dev/null 2>&1').read() if ret != 0 else ''
    mo_ok = ret == 0
    if not mo_ok:
        error_lines = errors.strip().split('\n')[:3]
        for e in error_lines:
            print(f"  MSGFMT: {e}")

    t_total = sum(1 for l in lines if l.startswith('msgstr "') and len(l) > 10)
    print(f"  {done}/{len(entries)} done, {t_total} total, .mo {'OK' if mo_ok else 'FAILED'}")
