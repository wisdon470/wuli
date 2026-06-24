# -*- coding: utf-8 -*-
"""
桐城中学叶老师教学 - 网站内容更新工具 v3
支持：作业（文本/文档下载）+ 答案（文本/图片）
"""
import re
import os
import subprocess

CONFIG_FILE = "教学网站_config.md"
INDEX_FILE = "index.html"

def read_config():
    """读取配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取作业
    homeworks = []
    for i in range(1, 20):  # 支持最多20个作业
        name_match = re.search(rf'作业{i}名称：(.+)', content)
        if not name_match:
            continue
        
        hw_type_match = re.search(rf'作业{i}类型：(.+)', content)
        hw_type = hw_type_match.group(1).strip() if hw_type_match else "text"
        
        if hw_type == "file":
            file_match = re.search(rf'作业{i}文件：(.+)', content)
            file_name = file_match.group(1).strip() if file_match else ""
            homeworks.append({
                'name': name_match.group(1).strip(),
                'type': 'file',
                'file': file_name
            })
        else:
            content_match = re.search(rf'作业{i}内容：\n([\s\S]*?)(?=作业\d+名称：|$)', content)
            hw_content = content_match.group(1).strip() if content_match else ""
            homeworks.append({
                'name': name_match.group(1).strip(),
                'type': 'text',
                'content': hw_content
            })
    
    # 读取答案
    answers = []
    for i in range(1, 30):  # 支持最多30个答案
        title_match = re.search(rf'答案{i}标题：(.+)', content)
        if not title_match:
            continue
        
        ans_type_match = re.search(rf'答案{i}类型：(.+)', content)
        ans_type = ans_type_match.group(1).strip() if ans_type_match else "text"
        
        if ans_type == "image":
            file_match = re.search(rf'答案{i}文件：(.+)', content)
            file_name = file_match.group(1).strip() if file_match else ""
            answers.append({
                'title': title_match.group(1).strip(),
                'type': 'image',
                'file': file_name
            })
        else:
            content_match = re.search(rf'答案{i}内容：\n([\s\S]*?)(?=答案\d+标题：|$)', content)
            ans_content = content_match.group(1).strip() if content_match else ""
            answers.append({
                'title': title_match.group(1).strip(),
                'type': 'text',
                'content': ans_content
            })
    
    return {'homeworks': homeworks, 'answers': answers}

def generate_html(config):
    """生成 HTML"""
    # 作业 HTML
    homework_html = ""
    for hw in config['homeworks']:
        if hw['type'] == 'file':
            # 检查文件是否存在
            file_exists = os.path.exists(hw['file'])
            if file_exists:
                homework_html += f'''
                        <div class="homework-item homework-file">
                            <span class="hw-icon">📄</span>
                            <span class="hw-name">{hw['name']}</span>
                            <a href="{hw['file']}" class="download-btn" download>⬇ 下载</a>
                        </div>'''
            else:
                homework_html += f'''
                        <div class="homework-item homework-file">
                            <span class="hw-icon">📄</span>
                            <span class="hw-name">{hw['name']}</span>
                            <span class="hw-note">(文件不存在)</span>
                        </div>'''
        else:
            content_html = hw['content'].replace('\n', '<br>')
            homework_html += f'''
                        <div class="homework-item homework-text">
                            <h4>{hw['name']}</h4>
                            <div class="hw-content">{content_html}</div>
                        </div>'''
    
    if not homework_html:
        homework_html = '<div class="placeholder">暂无作业</div>'
    
    # 答案 HTML
    answer_html = ""
    for ans in config['answers']:
        if ans['type'] == 'image':
            # 检查图片是否存在
            file_exists = os.path.exists(ans['file'])
            if file_exists:
                answer_html += f'''
                        <div class="answer-item">
                            <h4>{ans['title']}</h4>
                            <img src="{ans['file']}" alt="{ans['title']}">
                        </div>'''
            else:
                answer_html += f'''
                        <div class="answer-item answer-missing">
                            <h4>{ans['title']}</h4>
                            <p class="missing-note">(图片不存在: {ans['file']})</p>
                        </div>'''
        else:
            content_html = ans['content'].replace('\n', '<br>')
            answer_html += f'''
                        <div class="answer-item">
                            <h4>{ans['title']}</h4>
                            <div class="answer-text">{content_html}</div>
                        </div>'''
    
    if not answer_html:
        answer_html = '<div class="placeholder">暂无答案</div>'
    
    html = f'''<!DOCTYPE html>
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
            background: #f5f7fa;
            min-height: 100vh;
        }}
        header {{
            text-align: center;
            padding: 35px 20px;
            background: linear-gradient(135deg, #1e5799 0%, #2989d8 50%, #207cca 100%);
            color: white;
        }}
        h1 {{ font-size: 2em; margin-bottom: 8px; }}
        .subtitle {{ font-size: 0.95em; opacity: 0.9; }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 25px 20px;
        }}
        
        .two-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }}
        @media (max-width: 900px) {{
            .two-columns {{ grid-template-columns: 1fr; }}
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 16px 20px;
            font-size: 1.2em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .homework-header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
        .answer-header {{ background: linear-gradient(135deg, #11998e, #38ef7d); color: white; }}
        
        .card-body {{ padding: 20px; }}
        
        /* 作业样式 */
        .homework-item {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 12px;
            background: #f8f9ff;
            border-left: 4px solid #667eea;
        }}
        .homework-item h4 {{
            color: #667eea;
            margin-bottom: 8px;
            font-size: 1.05em;
        }}
        .homework-item.homework-file {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .hw-icon {{ font-size: 1.4em; }}
        .hw-name {{ flex: 1; font-weight: 500; }}
        .hw-note {{ color: #999; font-size: 0.9em; }}
        .hw-content {{ color: #555; font-size: 0.95em; }}
        
        .download-btn {{
            background: #667eea;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9em;
            transition: background 0.2s;
        }}
        .download-btn:hover {{ background: #5568d3; }}
        
        /* 答案样式 */
        .answer-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            border-left: 4px solid #11998e;
        }}
        .answer-item h4 {{
            color: #11998e;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        .answer-item img {{
            max-width: 100%;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .answer-text {{
            background: #e8f5e9;
            padding: 12px;
            border-radius: 6px;
            font-family: "Consolas", monospace;
            font-size: 0.9em;
            color: #2e7d32;
            white-space: pre-line;
        }}
        .answer-missing {{ border-left-color: #ccc; opacity: 0.7; }}
        .answer-missing h4 {{ color: #999; }}
        .missing-note {{ color: #e57373; font-size: 0.85em; }}
        
        .placeholder {{
            color: #999;
            text-align: center;
            padding: 40px;
            font-style: italic;
        }}
        
        footer {{
            text-align: center;
            padding: 25px;
            color: #888;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <header>
        <h1>桐城中学叶老师教学</h1>
        <p class="subtitle">高中物理 - 作业布置与答案核对</p>
    </header>
    
    <div class="container">
        <div class="two-columns">
            <div class="card">
                <div class="card-header homework-header">
                    <span>📝</span> 作业布置
                </div>
                <div class="card-body">
{homework_html}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header answer-header">
                    <span>✅</span> 答案核对
                </div>
                <div class="card-body">
{answer_html}
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>桐城中学 - 高中物理教学组</p>
        <p>&copy; 2026 叶老师</p>
    </footer>
</body>
</html>'''
    return html

def main():
    print("=" * 50)
    print("  [v3] Website Update Tool")
    print("=" * 50)
    print()
    
    # Read config
    print("[1] Reading config...")
    try:
        config = read_config()
        print(f"    - Homework: {len(config['homeworks'])} items")
        print(f"    - Answers:  {len(config['answers'])} items")
    except Exception as e:
        print(f"[ERROR] {e}")
        os.system("pause")
        return
    print()
    
    # Generate HTML
    print("[2] Generating webpage...")
    html = generate_html(config)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"    - Saved: {INDEX_FILE}")
    print()
    
    # Git push
    print("[3] Pushing to GitHub...")
    subprocess.run('git add -A', shell=True)
    result = subprocess.run('git commit -m "Update website"', shell=True, capture_output=True)
    result = subprocess.run('git push origin gh-pages', shell=True, capture_output=True)
    
    if result.returncode == 0:
        print("    - SUCCESS!")
        print()
        print("=" * 50)
        print("  [OK] Website Updated!")
        print("  https://wisdon470.github.io/wuli/")
        print("=" * 50)
    else:
        print("    - Network issue, changes saved locally")
        print("    - Please try again later")
    
    print()
    os.system("pause")

if __name__ == "__main__":
    main()
