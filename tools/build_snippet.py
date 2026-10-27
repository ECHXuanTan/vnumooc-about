"""Dựng _about_landing.liquid mới từ bản đang chạy + index.html/en/index.html mới.

- Đầu file (tới skip-link) và đuôi lấy từ bản đang chạy; chỉ thêm Oswald vào link Google Fonts.
- Thân = merge(VI, EN) rồi áp các chỉnh riêng cho theme, rút từ chênh lệch giữa merge(cặp HTML cũ 17caa82) và bản đang chạy.
"""
import difflib
import re
import sys

import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_about as M

live_path, old_vi, old_en, new_vi, new_en, out_path = sys.argv[1:7]
live = open(live_path, encoding='utf-8', newline='').read()
s = live.index('<a class="skip-link"')
e = live.index('</script>', live.index("'about/about.js'")) + len('</script>')
head, live_body, tail = live[:s], live[s:e], live[e:]

# 1. Chỉnh riêng cho theme: các đoạn khác (không chỉ khoảng trắng) giữa merge(cũ) và bản đang chạy
old_m = M.merge(M.body(old_vi), M.body(old_en))
tm, tl = M.TOKEN.findall(old_m), M.TOKEN.findall(live_body)
rules = []
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, tm, tl, autojunk=False).get_opcodes():
    if op == 'equal':
        continue
    a, b = ''.join(tm[i1:i2]), ''.join(tl[j1:j2])
    if re.sub(r'\s', '', a) == re.sub(r'\s', '', b):
        continue  # chỉ khác khoảng trắng: bản mới giữ cách của merge (đúng hơn)
    if a not in [r[0] for r in rules]:
        rules.append((a, b))
print('quy tắc chỉnh riêng cho theme:', len(rules))
for a, b in rules:
    print('  -', a[:110].replace('\n', '⏎'), '\n    →', b[:110].replace('\n', '⏎'))


LOGIN = re.compile(r'<a href="https://mooc\.vnuhcm\.edu\.vn/clients/login" target="_blank" rel="noopener noreferrer" class="([^"]*)">')


def adapt(t, report=False):
    t, n_login = LOGIN.subn(lambda m: '<a href="{{ linklist.login }}" class="' + m.group(1) + '">', t)
    missing = []
    for a, b in rules:
        if LOGIN.fullmatch(a):
            continue
        if a not in t:
            missing.append(a)
            continue
        t = t.replace(a, b)
    if report:
        print('link đăng nhập đổi sang linklist.login:', n_login)
        for a in missing:
            print('  quy tắc không còn chỗ áp:', a[:100].replace('\n', '⏎'))
    return t, n_login, missing


# Kiểm: áp quy tắc lên merge(cũ) phải ra bản đang chạy, chỉ còn khác khoảng trắng
chk = adapt(old_m)[0]
left = [op for op in difflib.SequenceMatcher(None, M.TOKEN.findall(chk), tl, autojunk=False).get_opcodes() if op[0] != 'equal']
assert all(re.sub(r'\s', '', ''.join(M.TOKEN.findall(chk)[o[1]:o[2]])) == re.sub(r'\s', '', ''.join(tl[o[3]:o[4]])) for o in left)
print('kiểm cặp cũ: còn', len(left), 'chỗ chỉ khác khoảng trắng')

# 2. Thân mới
vb, eb = M.body(new_vi), M.body(new_en)
merged = M.merge(vb, eb)
assert M.render(merged, 'vi') == M.asset(vb), 'dựng ngược VI không khớp'
assert M.render(merged, 'en') == M.asset(eb), 'dựng ngược EN không khớp'
print('dựng ngược: VI và EN khớp từng ký tự với hai file HTML')
new_body, n_login, missing = adapt(merged, report=True)
assert n_login == 2, n_login
for key_ in ('class="logo"', 'aria-haspopup="true"', 'href="index.html" class="is-active"', 'href="en/index.html"'):
    assert not any(key_ in a for a in missing), 'quy tắc chính không áp được: ' + key_
assert 'linklist.home' in new_body and '?locale=en' in new_body and '?locale=vi' in new_body

# 3. Đầu file: thêm Oswald
font_old = '<link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap" rel="stylesheet">'
assert head.count(font_old) == 1
head = head.replace(font_old, '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Patrick+Hand&display=swap" rel="stylesheet">')
c_old = '{%- comment -%} Patrick Hand (decorative) —'
assert head.count(c_old) == 1
head = head.replace(c_old, '{%- comment -%} Patrick Hand (decorative), Oswald (danh mục môn) —')

out = head + new_body + tail
# cân if/endif
assert out.count("{% if ") + out.count("{%- if ") == out.count("{% endif %}") + out.count("{%- endif -%}"), 'if/endif lệch'
open(out_path, 'w', encoding='utf-8', newline='').write(out)
print('ghi', out_path, len(out), 'ký tự', out.count('\n') + 1, 'dòng')
