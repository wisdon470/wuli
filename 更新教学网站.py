# -*- coding: utf-8 -*-
"""
桐城中学叶老师教学 - 网站更新工具 v4
简洁版：作业(文本) + 答案(文本/图片可点击放大)
"""
import re, os, subprocess

CONFIG_FILE = "教学网站_config.md"
INDEX_FILE = "index.html"

def read_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    homeworks = []
    for m in re.finditer(r'===作业\d+===\n标题：(.+?)\n内容：\n([\s\S]*?)===结束===', content):
        homeworks.append({'title': m.group(1).strip(), 'content': m.group(2).strip()})

    answers = []
    for m in re.finditer(r'===答案\d+===\n标题：(.+?)\n类型：(\w+)\n(?:文件：(.*?)\n)?(?:内容：\n([\s\S]*?))?===结束===', content):
        ans_type = m.group(2)
        if ans_type == 'image':
            answers.append({'title': m.group(1).strip(), 'type': 'image', 'file': (m.group(3) or '').strip()})
        else:
            answers.append({'title': m.group(1).strip(), 'type': 'text', 'content': (m.group(4) or '').strip()})

    return {'homeworks': homeworks, 'answers': answers}

def generate_html(config):
    # 作业 HTML
    hw_html = ""
    for hw in config['homeworks']:
        c = hw['content'].replace('\n', '<br>')
        hw_html += f'''                        <h3>{hw['title']}</h3>
                        <div class="hw-text">{c}</div>
'''
    if not hw_html:
        hw_html = '<div class="placeholder">暂无作业</div>'

    # 答案 HTML（图片支持点击放大）
    ans_html = ""
    for a in config['answers']:
        if a['type'] == 'image':
            exists = os.path.exists(a['file'])
            if exists:
                ans_html += f'''                        <div class="answer-item">
                            <h4>{a['title']}</h4>
                            <img src="{a['file']}" alt="{a['title']}" class="zoom-img" onclick="zoom(this)">
                        </div>
'''
            else:
                ans_html += f'''                        <div class="answer-item">
                            <h4>{a['title']}</h4>
                            <p class="missing">[图片不存在: {a['file']}]</p>
                        </div>
'''
        else:
            c = a.get('content','').replace('\n', '<br>')
            ans_html += f'''                        <div class="answer-item">
                            <h4>{a['title']}</h4>
                            <div class="ans-text">{c}</div>
                        </div>
'''
    if not ans_html:
        ans_html = '<div class="placeholder">暂无答案</div>'

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>桐城中学叶老师教学</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f0f2f5;
            min-height: 100vh;
        }}
        header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #1e5799 0%, #2989d8 50%, #207cca 100%);
            color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ font-size: 2.2em; margin-bottom: 10px; font-weight: 600; }}
        .subtitle {{ font-size: 1em; opacity: 0.9; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
        .two-columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        @media (max-width: 900px) {{ .two-columns {{ grid-template-columns: 1fr; }} }}
        .card {{ background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }}
        .card-header {{ padding: 20px 25px; font-size: 1.3em; font-weight: 600; display: flex; align-items: center; gap: 10px; color: white; }}
        .homework-header {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .answer-header {{ background: linear-gradient(135deg, #11998e, #38ef7d); }}
        .card-body {{ padding: 25px; min-height: 400px; }}

        /* 作业 */
        h3 {{ color: #667eea; margin: 18px 0 8px; font-size: 1.1em; }}
        h3:first-child {{ margin-top: 0; }}
        .hw-text {{ font-size: 1.05em; line-height: 2; color: #444; }}

        /* 答案 */
        .answer-content {{ display: flex; flex-direction: column; gap: 16px; }}
        .answer-item {{ background: #f8f9fa; border-radius: 8px; padding: 15px; border-left: 4px solid #11998e; }}
        .answer-item h4 {{ color: #11998e; margin-bottom: 10px; font-size: 1em; }}
        .ans-text {{ background: #e8f5e9; padding: 12px 15px; border-radius: 6px; font-family: Consolas, Monaco, monospace; font-size: 0.95em; color: #2e7d32; line-height: 1.6; }}

        /* 图片 - 可点击放大 */
        .zoom-img {{ max-width: 100%; border-radius: 6px; cursor: pointer; transition: transform 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .zoom-img:hover {{ transform: scale(1.02); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }}

        /* 图片放大遮罩 */
        #overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 9999; cursor: pointer; justify-content: center; align-items: center; }}
        #overlay img {{ max-width: 95%; max-height: 95%; object-fit: contain; border-radius: 8px; }}
        #overlay.show {{ display: flex; }}

        .missing {{ color: #e57373; font-style: italic; }}
        .placeholder {{ color: #999; font-style: italic; text-align: center; padding: 60px 20px; }}
        footer {{ text-align: center; padding: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <header>
        <h1>桐城中学叶老师教学</h1>
        <p class="subtitle">高中物理 · 作业布置与答案核对</p>
    </header>

    <!-- 图片放大遮罩 -->
    <div id="overlay" onclick="closeZoom()">
        <img id="zoomed-img" src="" alt="">
    </div>

    <div class="container">
        <div class="two-columns">
            <div class="card">
                <div class="card-header homework-header">
                    <span>&#128221;</span><span>作业布置</span>
                </div>
                <div class="card-body">
{hw_html}
                </div>
            </div>

            <div class="card">
                <div class="card-header answer-header">
                    <span>&#9989;</span><span>答案核对</span>
                </div>
                <div class="card-body">
                    <div class="answer-content">
{ans_html}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>桐城中学 · 高中物理教学组</p>
        <p>&copy; 2026 叶老师</p>
    </footer>

    <script>
    function zoom(img) {{
        document.getElementById('zoomed-img').src = img.src;
        document.getElementById('overlay').classList.add('show');
    }}
    function closeZoom() {{
        document.getElementById('overlay').classList.remove('show');
    }}
    // ESC 关闭
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') closeZoom();
    }});
    </script>
</body>
</html>'''

def main():
    print("=" * 50)
    print("  [v4] Website Update Tool")
    print("=" * 50)

    print("[1] Reading config...")
    try:
        config = read_config()
        print(f"    Homework: {len(config['homeworks'])}, Answers: {len(config['answers'])}")
    except Exception as e:
        print(f"[ERROR] {e}")
        os.system("pause")
        return

    print("[2] Generating webpage...")
    html = generate_html(config)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"    Saved: {INDEX_FILE}")

    print("[3] Pushing to GitHub...")
    subprocess.run('git add -A', shell=True, capture_output=True)
    subprocess.run('git commit -m "Update website"', shell=True, capture_output=True)
    r = subprocess.run('git push origin gh-pages', shell=True, capture_output=True)

    if r.returncode == 0:
        print("\n  [OK] Updated! https://wisdon470.github.io/wuli/")
    else:
        print("\n  [INFO] Network issue, saved locally. Try again later.")

    print()
    os.system("pause")

if __name__ == "__main__":
    main()
