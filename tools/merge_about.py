"""Trộn index.html (VI) + en/index.html (EN) thành thân snippet Liquid song ngữ của _about_landing.liquid.

Khung HTML dùng chung; chỗ chữ/thuộc tính khác nhau viết {% if ui_lang == 'en' %}EN{% else %}VI{% endif %};
chỗ cấu trúc khác nhau thì bọc nguyên đoạn. Đường dẫn assets/about/… → {{ 'about/…' | asset_url }}.
"""
import difflib
import html
import re

IF, ELSE, END = "{% if ui_lang == 'en' %}", "{% else %}", "{% endif %}"
TOKEN = re.compile(r'<!--.*?-->|<[^>]+>|[^<]+', re.S)
ATTR = re.compile(r'''([^\s=/>]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')


def body(path):
    t = open(path, encoding='utf-8').read()
    s = t.index('<a class="skip-link"')
    e = t.index('</script>', t.index('about.js')) + len('</script>')
    return t[s:e]


def asset(t):
    return re.sub(r'''(src|href)="(?:\.\./)?assets/about/([^"]+)"''', lambda m: f'''{m.group(1)}="{{{{ 'about/{m.group(2)}' | asset_url }}}}"''', t)


def tag_parts(tok):
    """<name a="1" b> → (name, [(attr, raw_value_or_None)], self_closing_suffix)"""
    m = re.match(r'<(/?[^\s>/]+)(.*?)(/?)>$', tok, re.S)
    name, rest, slash = m.group(1), m.group(2), m.group(3)
    attrs = [(a, v) for a, v in ATTR.findall(rest)]
    return name, attrs, slash


def key(tok):
    if tok.startswith('<!--'):
        return ('comment', tok)
    if tok.startswith('<'):
        name, attrs, _ = tag_parts(tok)
        return ('tag', name, tuple(a for a, _ in attrs))
    return ('text',)


def ws_split(a, b):
    """Tách khoảng trắng chung ở đầu/cuối để đặt ngoài khối if."""
    pre = 0
    while pre < min(len(a), len(b)) and a[pre] == b[pre] and a[pre].isspace():
        pre += 1
    suf = 0
    while suf < min(len(a), len(b)) - pre and a[len(a) - 1 - suf] == b[len(b) - 1 - suf] and a[len(a) - 1 - suf].isspace():
        suf += 1
    return a[:pre], a[pre:len(a) - suf], b[pre:len(b) - suf], a[len(a) - suf:]


def merge_tag(vi, en):
    if vi == en:
        return vi
    nv, av, sv = tag_parts(vi)
    ne, ae, se = tag_parts(en)
    out = []
    for (a, v1), (_, v2) in zip(av, ae):
        if v1 == v2:
            out.append(a if v1 == '' else f'{a}={v1}')
        else:
            x1, x2 = v1.strip('"'), v2.strip('"')
            out.append(f'{a}="{IF}{x2}{ELSE}{x1}{END}"')
    return f'<{nv}' + ''.join(' ' + o for o in out) + f'{sv}>'


def merge(vi_html, en_html):
    tv, te = TOKEN.findall(asset(vi_html)), TOKEN.findall(asset(en_html))
    kv, ke = [key(t) for t in tv], [key(t) for t in te]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, kv, ke, autojunk=False).get_opcodes():
        if op == 'equal':
            for a, b in zip(tv[i1:i2], te[j1:j2]):
                if a == b:
                    out.append(a)
                elif a.startswith('<'):
                    out.append(merge_tag(a, b))
                else:
                    p, x1, x2, s = ws_split(a, b)
                    out.append(f'{p}{IF}{x2}{ELSE}{x1}{END}{s}')
        else:
            a, b = ''.join(tv[i1:i2]), ''.join(te[j1:j2])
            p, x1, x2, s = ws_split(a, b)
            out.append(f'{p}{IF}{x2}{ELSE}{x1}{END}{s}')
    return ''.join(out)


def render(liquid, lang):
    """Dựng ngược một ngôn ngữ từ thân Liquid (chỉ hiểu đúng mẫu if/else/endif do merge sinh ra)."""
    pat = re.compile(re.escape(IF) + r'(.*?)' + re.escape(ELSE) + r'(.*?)' + re.escape(END), re.S)
    return pat.sub(lambda m: m.group(1) if lang == 'en' else m.group(2), liquid)
