"""Kiểm tra bản dịch: python3 tools/check.py [NN ...]  (không tham số = tất cả chunk)."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VI = re.compile(r'[ăâđêôơưàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ]', re.I)

def check(n):
    src = json.load(open(os.path.join(ROOT, 'chunks', n + '.json'), encoding='utf-8'))
    p = os.path.join(ROOT, 'out', n + '.json')
    if not os.path.exists(p):
        return ['thiếu file out/%s.json' % n]
    try:
        out = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        return ['JSON lỗi: %s' % e]
    errs = []
    miss = [k for k in src if not str(out.get(k, '')).strip()]
    extra = [k for k in out if k not in src]
    if miss: errs.append('thiếu %d ID: %s' % (len(miss), ' '.join(miss[:30])))
    if extra: errs.append('thừa ID: %s' % ' '.join(extra[:30]))
    for k, en in src.items():
        vi = str(out.get(k, ''))
        if not vi.strip():
            continue
        if len(en) > 60 and not VI.search(vi):
            errs.append('%s chưa dịch (không có dấu tiếng Việt)' % k)
        elif len(en) > 80 and not (0.6 <= len(vi) / len(en) <= 2.5):
            errs.append('%s độ dài bất thường (%d → %d ký tự)' % (k, len(en), len(vi)))
    return errs

args = sys.argv[1:]
if args == ['--existing']:   # dùng cho check của AgentHub: chỉ kiểm các chunk đã có out/
    names = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, 'out')) if f.endswith('.json'))
    if not names:
        print('chưa có file out/*.json nào'); sys.exit(1)
else:
    names = args or sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, 'chunks')))
bad = 0
for n in names:
    e = check(n)
    print('%s: %s' % (n, 'OK' if not e else 'LỖI'))
    for x in e: print('   -', x)
    bad += bool(e)
sys.exit(1 if bad else 0)
