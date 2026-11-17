"""Ghép bản song ngữ: python3 tools/merge.py  → project_management_2nd_edition_song_ngu.md"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blocks = json.load(open(os.path.join(ROOT, 'tools', 'blocks.json'), encoding='utf-8'))
vi = {}
for f in sorted(os.listdir(os.path.join(ROOT, 'out'))):
    if f.endswith('.json'):
        vi.update(json.load(open(os.path.join(ROOT, 'out', f), encoding='utf-8')))
# map tiêu đề EN → VI cho mục lục
head_vi = {b['raw'].strip()[3:].strip(): vi.get(b['id'], '') for b in blocks if b['kind'] == 'heading'}
missing = 0
res = []
for b in blocks:
    raw = b['raw']
    if b['kind'] == 'heading':
        en = raw.strip()[3:].strip(); t = vi.get(b['id'], '').strip()
        raw = '## %s' % en + (' / %s' % t if t and t != en else '')
        missing += not t
    elif b['kind'] == 'text':
        t = vi.get(b['id'], '').strip()
        if t:
            raw = raw.rstrip() + '\n\n' + '\n'.join('> ' + l if l.strip() else '>' for l in t.split('\n'))
        else:
            missing += 1
    else:
        m = re.fullmatch(r'\* \[(.+)\]\((#chapter-\d+)\)', raw.strip())
        if m and head_vi.get(m.group(1)) and head_vi[m.group(1)] != m.group(1):
            raw = '* [%s / %s](%s)' % (m.group(1), head_vi[m.group(1)], m.group(2))
    res.append(raw + b['sep'])
out = os.path.join(ROOT, 'project_management_2nd_edition_song_ngu.md')
open(out, 'w', encoding='utf-8').write(''.join(res))
print('Đã ghi', out, '| đoạn chưa có bản dịch:', missing)
