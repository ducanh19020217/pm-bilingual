#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tạo trang HTML song song 2 cột đối chiếu (Side-by-side Dual Viewer)
cho sách Project Management, 2nd Edition (Abdullah Oguz).
"""

import os
import sys
import json
import re
import html
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCKS_PATH = os.path.join(ROOT, 'tools', 'blocks.json')
OUT_DIR = os.path.join(ROOT, 'out')
OUTPUT_HTML = os.path.join(ROOT, 'project_management_song_ngu_song_song.html')
WORKSPACE_HTML = os.path.join(os.path.dirname(ROOT), 'project_management_song_ngu_song_song.html')

def md_to_html(text):
    if not text:
        return ""
    # Convert markdown to html
    # Use standard extensions for tables, fenced_code
    return markdown.markdown(text, extensions=['tables', 'fenced_code'])

def main():
    print("Đang tải blocks và các bản dịch...")
    with open(BLOCKS_PATH, 'r', encoding='utf-8') as f:
        blocks = json.load(f)

    vi = {}
    for fname in sorted(os.listdir(OUT_DIR)):
        if fname.endswith('.json'):
            fpath = os.path.join(OUT_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                vi.update(json.load(f))

    print(f"Tổng số block: {len(blocks)}, Tổng số đoạn dịch: {len(vi)}")

    # Xây dựng danh sách mục lục (TOC)
    toc_items = []
    for b in blocks:
        if b['kind'] == 'heading':
            bid = b.get('id', '')
            raw = b['raw'].strip()
            # bỏ ## đầu dòng
            en_title = re.sub(r'^#+\s*', '', raw).strip()
            vi_title = vi.get(bid, '').strip()
            toc_items.append({
                'id': bid,
                'en': en_title,
                'vi': vi_title
            })

    print(f"Tổng số mục tiêu đề (Headings): {len(toc_items)}")

    # Sinh HTML
    rows_html = []
    current_chapter_anchor = ""

    for b in blocks:
        kind = b['kind']
        bid = b.get('id', '')
        raw = b['raw']

        # Xử lý các thẻ anchor <a id="chapter-XX" ...> trong skip
        if kind == 'skip':
            m_anchor = re.search(r'<a id="([^"]+)" name="[^"]*"></a>', raw)
            if m_anchor:
                current_chapter_anchor = m_anchor.group(1)
                rows_html.append(f'<div class="anchor-target" id="{current_chapter_anchor}"></div>')
                continue
            
            # Bỏ qua dòng [↑ Về mục lục] hoặc --- đơn thuần, hoặc render separator
            if '[↑ Về mục lục]' in raw:
                rows_html.append(f'''
                <div class="row-separator">
                    <a href="#muc-luc" class="back-to-top">↑ Về đầu trang / Mục lục</a>
                </div>
                ''')
                continue
            elif raw.strip() == '---':
                rows_html.append('<hr class="section-divider"/>')
                continue
            elif raw.strip().startswith('# PROJECT MANAGEMENT'):
                rows_html.append(f'''
                <div class="book-banner">
                    <h1>PROJECT MANAGEMENT, 2ND EDITION</h1>
                    <div class="book-subtitle">Bản đối chiếu song ngữ Anh – Việt (Side-by-Side Dual View)</div>
                    <div class="book-author">Tác giả: Abdullah Oguz</div>
                </div>
                ''')
                continue
            elif raw.strip().startswith('* ['):
                # Khối mục lục markdown cũ - có thể ẩn vì ta đã có Sidebar TOC chuyên dụng
                continue

        if kind == 'heading':
            en_text = re.sub(r'^#+\s*', '', raw).strip()
            vi_text = vi.get(bid, '').strip()
            level = 2
            if raw.startswith('###'):
                level = 3
            elif raw.startswith('####'):
                level = 4

            row_id = f"heading-{bid}"
            rows_html.append(f'''
            <div class="bilingual-heading level-{level}" id="{row_id}">
                <div class="heading-col en">
                    <span class="heading-badge">EN</span>
                    <span class="heading-text">{html.escape(en_text)}</span>
                </div>
                <div class="heading-col vi">
                    <span class="heading-badge">VI</span>
                    <span class="heading-text">{html.escape(vi_text if vi_text else en_text)}</span>
                </div>
            </div>
            ''')
        elif kind == 'text':
            en_raw = raw.strip()
            vi_raw = vi.get(bid, '').strip()

            en_html = md_to_html(en_raw)
            vi_html = md_to_html(vi_raw) if vi_raw else '<em style="color:#888;">(Chưa có bản dịch)</em>'

            row_id = f"row-{bid}"
            rows_html.append(f'''
            <div class="bilingual-row" id="{row_id}" data-id="{bid}">
                <div class="cell col-en">
                    <div class="cell-content">{en_html}</div>
                </div>
                <div class="cell col-vi">
                    <div class="cell-content">{vi_html}</div>
                </div>
            </div>
            ''')

    # Render TOC links
    toc_links = []
    for item in toc_items:
        title_display = html.escape(item['en'])
        if item['vi'] and item['vi'] != item['en']:
            title_display += f' <span class="toc-vi">({html.escape(item["vi"])})</span>'
        target_id = f"heading-{item['id']}"
        toc_links.append(f'<li><a href="#{target_id}">{title_display}</a></li>')

    toc_html = "\n".join(toc_links)
    content_html = "\n".join(rows_html)

    full_html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Management, 2nd Edition — Song ngữ Anh - Việt</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-header: rgba(255, 255, 255, 0.95);
            --border-color: #e2e8f0;
            --border-hover: #93c5fd;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --highlight-row: #eff6ff;
            --primary: #2563eb;
            --primary-light: #dbeafe;
            --badge-en: #e0e7ff;
            --badge-en-text: #3730a3;
            --badge-vi: #dcfce7;
            --badge-vi-text: #166534;
            --font-serif: 'Merriweather', Georgia, serif;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-size: 16px;
            --sidebar-width: 340px;
        }}

        [data-theme="sepia"] {{
            --bg-body: #fbf7ee;
            --bg-card: #f4ecd8;
            --bg-header: rgba(244, 236, 216, 0.96);
            --border-color: #e6dac3;
            --border-hover: #d2b48c;
            --text-main: #382c1e;
            --text-muted: #736148;
            --highlight-row: #eae0c8;
            --primary: #945318;
            --primary-light: #fbeee0;
            --badge-en: #edd9c0;
            --badge-en-text: #633c16;
            --badge-vi: #d8e5cb;
            --badge-vi-text: #2f5419;
        }}

        [data-theme="dark"] {{
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --bg-header: rgba(30, 41, 59, 0.95);
            --border-color: #334155;
            --border-hover: #60a5fa;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --highlight-row: #1e3a5f;
            --primary: #3b82f6;
            --primary-light: #1e293b;
            --badge-en: #312e81;
            --badge-en-text: #c7d2fe;
            --badge-vi: #064e3b;
            --badge-vi-text: #a7f3d0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-sans);
            font-size: var(--font-size);
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.65;
            transition: background-color 0.2s, color 0.2s;
        }}

        /* Header thanh điều khiển trên cùng */
        header.top-navbar {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: var(--bg-header);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .brand-section {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .btn-toggle-sidebar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s;
        }}

        .btn-toggle-sidebar:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}

        .brand-title {{
            font-size: 15px;
            font-weight: 700;
            letter-spacing: -0.2px;
            white-space: nowrap;
        }}

        .controls-section {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .btn-control {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.15s;
        }}

        .btn-control:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}

        .mode-selector select {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
        }}

        /* Bố cục chính */
        .layout-wrapper {{
            display: flex;
            min-height: calc(100vh - 57px);
        }}

        /* Sidebar Mục lục */
        aside.sidebar {{
            width: var(--sidebar-width);
            flex-shrink: 0;
            border-right: 1px solid var(--border-color);
            background: var(--bg-card);
            padding: 20px 16px;
            height: calc(100vh - 57px);
            position: sticky;
            top: 57px;
            overflow-y: auto;
            transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        aside.sidebar.collapsed {{
            margin-left: calc(-1 * var(--sidebar-width));
        }}

        .sidebar-header {{
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        .sidebar-search {{
            width: 100%;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-body);
            color: var(--text-main);
            font-size: 13px;
            margin-bottom: 16px;
        }}

        .sidebar-toc ul {{
            list-style: none;
        }}

        .sidebar-toc li {{
            margin-bottom: 6px;
        }}

        .sidebar-toc a {{
            color: var(--text-main);
            text-decoration: none;
            font-size: 13px;
            display: block;
            padding: 6px 10px;
            border-radius: 6px;
            line-height: 1.4;
            transition: background 0.15s;
        }}

        .sidebar-toc a:hover {{
            background: var(--highlight-row);
            color: var(--primary);
        }}

        .toc-vi {{
            color: var(--text-muted);
            font-size: 12px;
            display: block;
            margin-top: 2px;
        }}

        /* Khung hiển thị nội dung song ngữ */
        main.content-area {{
            flex-grow: 1;
            padding: 24px 36px;
            max-width: 1600px;
            margin: 0 auto;
            width: 100%;
        }}

        /* Banner sách */
        .book-banner {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
        }}

        .book-banner h1 {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
            color: var(--primary);
        }}

        .book-subtitle {{
            font-size: 16px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .book-author {{
            font-size: 15px;
            font-weight: 600;
        }}

        /* Thanh tiêu đề cột EN | VI */
        .columns-header {{
            position: sticky;
            top: 57px;
            z-index: 100;
            display: flex;
            gap: 20px;
            padding: 10px 16px;
            background: var(--bg-header);
            backdrop-filter: blur(8px);
            border-bottom: 2px solid var(--border-color);
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }}

        .col-header-cell {{
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Hàng tiêu đề chương */
        .bilingual-heading {{
            display: flex;
            gap: 20px;
            margin: 36px 0 16px;
            padding: 16px 18px;
            border-radius: 8px;
            background: var(--bg-card);
            border-left: 5px solid var(--primary);
            border-top: 1px solid var(--border-color);
            border-right: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            scroll-margin-top: 110px;
        }}

        .bilingual-heading.level-2 {{
            font-size: 20px;
            font-weight: 700;
        }}

        .bilingual-heading.level-3 {{
            font-size: 17px;
            font-weight: 600;
        }}

        .heading-col {{
            flex: 1;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        .heading-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 6px;
            border-radius: 4px;
            flex-shrink: 0;
            margin-top: 4px;
        }}

        .en .heading-badge {{
            background: var(--badge-en);
            color: var(--badge-en-text);
        }}

        .vi .heading-badge {{
            background: var(--badge-vi);
            color: var(--badge-vi-text);
        }}

        /* Hàng nội dung song ngữ */
        .bilingual-row {{
            display: flex;
            gap: 20px;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 6px;
            transition: background 0.12s ease;
            content-visibility: auto;
            contain-intrinsic-size: 80px;
        }}

        .bilingual-row:hover {{
            background-color: var(--highlight-row);
            box-shadow: 0 0 0 1px var(--border-hover);
        }}

        .bilingual-row.active {{
            background-color: var(--highlight-row);
            box-shadow: 0 0 0 2px var(--primary);
        }}

        .cell {{
            flex: 1;
            min-width: 0;
        }}

        .col-en {{
            font-family: var(--font-sans);
            color: var(--text-main);
        }}

        .col-vi {{
            font-family: var(--font-sans);
            color: var(--text-main);
        }}

        .cell-content p {{
            margin-bottom: 8px;
        }}

        .cell-content p:last-child {{
            margin-bottom: 0;
        }}

        .cell-content ul, .cell-content ol {{
            padding-left: 20px;
            margin-bottom: 8px;
        }}

        .cell-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 13px;
        }}

        .cell-content th, .cell-content td {{
            border: 1px solid var(--border-color);
            padding: 6px 10px;
        }}

        .cell-content th {{
            background: var(--highlight-row);
        }}

        .section-divider {{
            border: 0;
            height: 1px;
            background: var(--border-color);
            margin: 24px 0;
        }}

        .row-separator {{
            text-align: right;
            padding: 8px 16px;
            margin-bottom: 12px;
        }}

        .back-to-top {{
            font-size: 12px;
            color: var(--text-muted);
            text-decoration: none;
        }}

        .back-to-top:hover {{
            color: var(--primary);
        }}

        /* Chế độ xem lọc 1 cột */
        body.view-only-en .col-vi,
        body.view-only-en .heading-col.vi,
        body.view-only-en .col-header-vi {{
            display: none !important;
        }}

        body.view-only-vi .col-en,
        body.view-only-vi .heading-col.en,
        body.view-only-vi .col-header-en {{
            display: none !important;
        }}

        /* Responsive */
        @media (max-width: 900px) {{
            .columns-header {{
                display: none;
            }}
            .bilingual-heading,
            .bilingual-row {{
                flex-direction: column;
                gap: 10px;
            }}
            aside.sidebar {{
                position: fixed;
                left: 0;
                top: 57px;
                z-index: 1001;
                box-shadow: 4px 0 16px rgba(0,0,0,0.1);
            }}
            main.content-area {{
                padding: 16px 12px;
            }}
        }}
    </style>
</head>
<body id="muc-luc">

    <header class="top-navbar">
        <div class="brand-section">
            <button class="btn-toggle-sidebar" id="btnToggleSidebar" title="Đóng/Mở Mục lục">
                <span>☰</span> <span>Mục lục</span>
            </button>
            <div class="brand-title">Project Management (2nd Edition) — Song ngữ</div>
        </div>

        <div class="controls-section">
            <!-- Chế độ hiển thị -->
            <div class="mode-selector">
                <select id="selectViewMode" title="Chế độ cột">
                    <option value="both">⚡ Song song 2 cột (EN | VI)</option>
                    <option value="en">Chỉ tiếng Anh (EN)</option>
                    <option value="vi">Chỉ tiếng Việt (VI)</option>
                </select>
            </div>

            <!-- Giao diện màu -->
            <div class="mode-selector">
                <select id="selectTheme" title="Giao diện đọc">
                    <option value="light">☀️ Sáng</option>
                    <option value="sepia">📖 Giấy Sepia</option>
                    <option value="dark">🌙 Ban đêm</option>
                </select>
            </div>

            <!-- Kích cỡ chữ -->
            <button class="btn-control" id="btnFontDec" title="Giảm cỡ chữ">A-</button>
            <button class="btn-control" id="btnFontInc" title="Tăng cỡ chữ">A+</button>
        </div>
    </header>

    <div class="layout-wrapper">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">Danh sách chương</div>
            <input type="text" id="inputTocSearch" class="sidebar-search" placeholder="🔍 Tìm mục/chương...">
            <nav class="sidebar-toc">
                <ul id="tocList">
                    {toc_html}
                </ul>
            </nav>
        </aside>

        <main class="content-area">
            <div class="columns-header">
                <div class="col-header-cell col-header-en">
                    <span class="heading-badge en">EN</span>
                    <span>Bản gốc tiếng Anh</span>
                </div>
                <div class="col-header-cell col-header-vi">
                    <span class="heading-badge vi">VI</span>
                    <span>Bản dịch tiếng Việt</span>
                </div>
            </div>

            <div id="contentList">
                {content_html}
            </div>
        </main>
    </div>

    <script>
        // Toggle Sidebar
        const btnToggleSidebar = document.getElementById('btnToggleSidebar');
        const sidebar = document.getElementById('sidebar');
        btnToggleSidebar.addEventListener('click', () => {{
            sidebar.classList.toggle('collapsed');
        }});

        // Theme switch
        const selectTheme = document.getElementById('selectTheme');
        selectTheme.addEventListener('change', (e) => {{
            const val = e.target.value;
            if (val === 'light') {{
                document.documentElement.removeAttribute('data-theme');
            }} else {{
                document.documentElement.setAttribute('data-theme', val);
            }}
            localStorage.setItem('pm_theme', val);
        }});
        const savedTheme = localStorage.getItem('pm_theme');
        if (savedTheme) {{
            selectTheme.value = savedTheme;
            if (savedTheme !== 'light') document.documentElement.setAttribute('data-theme', savedTheme);
        }}

        // Font size control
        let currentFontSize = 16;
        const btnFontDec = document.getElementById('btnFontDec');
        const btnFontInc = document.getElementById('btnFontInc');
        btnFontDec.addEventListener('click', () => {{
            if (currentFontSize > 13) {{
                currentFontSize -= 1;
                document.documentElement.style.setProperty('--font-size', currentFontSize + 'px');
            }}
        }});
        btnFontInc.addEventListener('click', () => {{
            if (currentFontSize < 24) {{
                currentFontSize += 1;
                document.documentElement.style.setProperty('--font-size', currentFontSize + 'px');
            }}
        }});

        // View Mode (both / en / vi)
        const selectViewMode = document.getElementById('selectViewMode');
        selectViewMode.addEventListener('change', (e) => {{
            document.body.classList.remove('view-only-en', 'view-only-vi');
            if (e.target.value === 'en') {{
                document.body.classList.add('view-only-en');
            }} else if (e.target.value === 'vi') {{
                document.body.classList.add('view-only-vi');
            }}
        }});

        // Row click to active highlight
        document.getElementById('contentList').addEventListener('click', (e) => {{
            const row = e.target.closest('.bilingual-row');
            if (row) {{
                document.querySelectorAll('.bilingual-row.active').forEach(r => r.classList.remove('active'));
                row.classList.add('active');
            }}
        }});

        // Filter TOC
        const inputTocSearch = document.getElementById('inputTocSearch');
        const tocList = document.getElementById('tocList');
        inputTocSearch.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            const items = tocList.querySelectorAll('li');
            items.forEach(li => {{
                const text = li.textContent.toLowerCase();
                li.style.display = text.includes(query) ? '' : 'none';
            }});
        }});
    </script>
</body>
</html>
'''

    print("Đang ghi file HTML...")
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Đã xuất: {OUTPUT_HTML} (Kích thước: {os.path.getsize(OUTPUT_HTML) / (1024*1024):.2f} MB)")

    with open(WORKSPACE_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Đã xuất: {WORKSPACE_HTML} (Kích thước: {os.path.getsize(WORKSPACE_HTML) / (1024*1024):.2f} MB)")

if __name__ == '__main__':
    main()
