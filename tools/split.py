"""Tách sách thành các đoạn có ID, bỏ đoạn không cần dịch, gộp đoạn trùng, chia chunk theo mục."""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'project_management_2nd_edition.md')
TARGET_WORDS = 5000

SKIP = re.compile(r'^(<a id=|---$|\[↑|\* \[|#\s|https?://\S+\s*↵?$|↵$)')
REF = re.compile(r'(\(\d{4}[a-z]?\)|doi\.org|Retrieved|https?://).*↵\s*$', re.S)

def classify(block):
    s = block.strip()
    if s.startswith('## '):
        return 'heading'
    if SKIP.match(s) or REF.search(s) or not re.search(r'[A-Za-z]{3}', s):
        return 'skip'
    # đoạn chỉ là chú thích ngắn kiểu URL + ↵ trên nhiều dòng
    if re.fullmatch(r'(https?://\S+\s*)+↵?', s):
        return 'skip'
    return 'text'

def main():
    text = open(SRC, encoding='utf-8').read()
    parts = re.split(r'(\n\s*\n)', text)          # giữ nguyên dấu phân cách
    blocks, ids, src_of = [], {}, {}
    for i in range(0, len(parts), 2):
        b = parts[i]; sep = parts[i + 1] if i + 1 < len(parts) else ''
        kind = classify(b) if b.strip() else 'skip'
        pid = None
        if kind != 'skip':
            key = b.strip()[3:].strip() if kind == 'heading' else b.strip()
            if key in ids:
                pid = ids[key]
            else:
                pid = 'p%04d' % (len(ids) + 1); ids[key] = pid; src_of[pid] = (key, kind)
        blocks.append({'raw': b, 'sep': sep, 'kind': kind, 'id': pid})
    # chia chunk: chỉ cắt ở tiêu đề "## " khi đã đủ số từ
    chunks, cur, words, done = [], {}, 0, set()
    for bl in blocks:
        pid = bl['id']
        if (bl['kind'] == 'heading' and words >= TARGET_WORDS) or (bl['kind'] == 'text' and words >= 7000):
            chunks.append(cur); cur, words = {}, 0
        if not pid or pid in done:
            continue
        cur[pid] = src_of[pid][0]; done.add(pid); words += len(src_of[pid][0].split())
    if cur:
        chunks.append(cur)
    for f in os.listdir(os.path.join(ROOT, 'chunks')):
        os.remove(os.path.join(ROOT, 'chunks', f))
    for n, c in enumerate(chunks, 1):
        with open(os.path.join(ROOT, 'chunks', '%02d.json' % n), 'w', encoding='utf-8') as fh:
            json.dump(c, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'tools', 'blocks.json'), 'w', encoding='utf-8') as fh:
        json.dump(blocks, fh, ensure_ascii=False)
    for n, c in enumerate(chunks, 1):
        w = sum(len(v.split()) for v in c.values())
        first = next(iter(c.values()))[:50]
        print('%02d  %4d đoạn  %5d từ  %s' % (n, len(c), w, first))
    print('Tổng ID:', len(ids))

main()
