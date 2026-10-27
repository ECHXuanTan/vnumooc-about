"""Render tối giản snippet _about_landing.liquid cho một ngôn ngữ để xem trước (không phải Liquid đầy đủ)."""
import re, sys
src, lang, assets, out = sys.argv[1:5]
t = open(src, encoding='utf-8').read()
t = re.sub(r'\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}', '', t, flags=re.S)
t = re.sub(r'\{%-?\s*assign[^%]*-?%\}', '', t)
t = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*asset_url\s*\}\}", lambda m: f'file://{assets}/{m.group(1)}', t)
t = t.replace("{{ 'layouts.theme.language' | translate }}", 'Ngôn ngữ' if lang == 'vi' else 'Language')
t = t.replace('{{ linklist.home }}', '/').replace('{{ linklist.login }}', '/clients/login')
left = re.findall(r'\{\{.*?\}\}', t)
assert not left, left[:3]
# if/else/endif lồng nhau theo ui_lang
out_s, stack, pos = [], [], 0
for m in re.finditer(r"\{%-?\s*(if|else|endif)\s*(?:ui_lang\s*==\s*'(\w+)')?\s*-?%\}", t):
    if all(stack):
        out_s.append(t[pos:m.start()])
    kind = m.group(1)
    if kind == 'if':
        stack.append(m.group(2) == lang)
    elif kind == 'else':
        stack[-1] = not stack[-1]
    else:
        stack.pop()
    pos = m.end()
out_s.append(t[pos:])
assert not stack
html = ''.join(out_s)
assert '{%' not in html, html[html.index('{%')-50:html.index('{%')+80]
open(out, 'w', encoding='utf-8').write(f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>{html}</body></html>')
print(out, len(html))
