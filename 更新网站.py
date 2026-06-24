# -*- coding: utf-8 -*-
"""
桐城中学叶老师教学 - 网站内容更新工具
读取 config.md 配置，生成 index.html 并推送到 GitHub
"""
import re
import os
import base64
import json
import urllib.request
import sys

# 设置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

# ========== 配置区 ==========
GITHUB_TOKEN = "github_pat_11CGUXXAQ05RxD4emvuJh_lwmK5PmTNaepcbcWeLb9wIgePM6aeUZRXOHztAwwtvuJ464TG3KAAslWcmY"
REPO_OWNER = "wisdon470"
REPO_NAME = "wuli"
BRANCH = "gh-pages"
CONFIG_FILE = "config.md"
INDEX_FILE = "index.html"
# ============================

def read_config():
    """读取配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析作业标题
    homework_title = re.search(r'作业标题：(.+)', content)
    homework_title = homework_title.group(1).strip() if homework_title else "今日作业"
    
    # 解析作业列表
    homework_section = re.search(r'作业列表：\n([\s\S]*?)(?=本周重点标题：|$)', content)
    homework_items = []
    if homework_section:
        items = re.findall(r'- (.+)', homework_section.group(1))
        homework_items = [item.strip() for item in items]
    
    # 解析本周重点
    week_title = re.search(r'本周重点标题：(.+)', content)
    week_title = week_title.group(1).strip() if week_title else "本周重点"
    
    week_section = re.search(r'本周重点列表：\n([\s\S]*?)(?=温馨提示：|$)', content)
    week_items = []
    if week_section:
        items = re.findall(r'- (.+)', week_section.group(1))
        week_items = [item.strip() for item in items]
    
    # 解析温馨提示
    tip = re.search(r'温馨提示：(.+)', content)
    tip_text = tip.group(1).strip() if tip else ""
    
    # 解析答案列表
    answers = []
    raw_answers = re.split(r'\n===\s*$', content, flags=re.MULTILINE)
    for block in raw_answers:
        if '答案' in block and '类型：' in block:
            title_match = re.search(r'答案\d+：(.+)', block)
            type_match = re.search(r'类型：(.+)', block)
            content_match = re.search(r'内容：\n([\s\S]+)', block)
            
            if title_match and type_match:
                answer_type = type_match.group(1).strip()
                answer_content = content_match.group(1).strip() if content_match else ""
                answers.append({
                    'title': title_match.group(1).strip(),
                    'type': answer_type,
                    'content': answer_content
                })
    
    return {
        'homework_title': homework_title,
        'homework_items': homework_items,
        'week_title': week_title,
        'week_items': week_items,
        'tip': tip_text,
        'answers': answers
    }

def generate_html(config):
    """生成 HTML 页面"""
    # 生成作业列表 HTML
    homework_html = ""
    for item in config['homework_items']:
        homework_html += f"                            <li>{item}</li>\n"
    
    week_html = ""
    for item in config['week_items']:
        week_html += f"                            <li>{item}</li>\n"
    
    # 生成答案 HTML
    answers_html = ""
    for answer in config['answers']:
        if answer['type'] == 'image':
            answers_html += f'''                        <div class="answer-item">
                            <h4>{answer['title']}</h4>
                            <img src="{answer['content']}" alt="{answer['title']}">
                        </div>
'''
        else:
            content_lines = answer['content'].replace('\n', '<br>')
            answers_html += f'''                        <div class="answer-item">
                            <h4>{answer['title']}</h4>
                            <div class="answer-text">{content_lines}</div>
                        </div>
'''
    
    # 如果没有答案，显示占位
    if not answers_html:
        answers_html = '                        <div class="placeholder">暂无答案，稍后更新</div>\n'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>桐城中学叶老师教学</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
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
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        
        .two-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        @media (max-width: 900px) {{
            .two-columns {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 20px 25px;
            font-size: 1.3em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .homework-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .answer-header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        
        .card-body {{
            padding: 25px;
            min-height: 400px;
        }}
        
        .homework-content {{
            font-size: 1.05em;
            line-height: 2;
        }}
        
        .homework-content h3 {{
            color: #667eea;
            margin: 20px 0 10px;
            font-size: 1.1em;
        }}
        
        .homework-content ul {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}
        
        .homework-content li {{
            margin: 8px 0;
        }}
        
        .answer-content {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .answer-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
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
            padding: 12px 15px;
            border-radius: 6px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 0.95em;
            color: #2e7d32;
            white-space: pre-line;
        }}
        
        .placeholder {{
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 60px 20px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .icon {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <header>
        <h1>桐城中学叶老师教学</h1>
        <p class="subtitle">高中物理 · 作业布置与答案核对</p>
    </header>
    
    <div class="container">
        <div class="two-columns">
            <!-- 作业布置区域 -->
            <div class="card">
                <div class="card-header homework-header">
                    <span class="icon">[emoji]</span>
                    <span>作业布置</span>
                </div>
                <div class="card-body">
                    <div class="homework-content">
                        <h3>{config['homework_title']}</h3>
                        <ul>
{homework_html}                        </ul>
                        
                        <h3>{config['week_title']}</h3>
                        <ul>
{week_html}                        </ul>
                        
                        <h3>温馨提示</h3>
                        <p>{config['tip']}</p>
                    </div>
                </div>
            </div>
            
            <!-- 答案核对区域 -->
            <div class="card">
                <div class="card-header answer-header">
                    <span class="icon">[emoji]</span>
                    <span>答案核对</span>
                </div>
                <div class="card-body">
                    <div class="answer-content">
{answers_html}                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>桐城中学 · 高中物理教学组</p>
        <p>&copy; 2026 叶老师</p>
    </footer>
</body>
</html>'''
    return html

def get_file_sha(path):
    """获取 GitHub 上文件的 SHA"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python Script"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data['sha']
    except:
        return None

def upload_to_github(content, path, message):
    """上传文件到 GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    
    # Base64 编码
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    
    # 获取 SHA（如果文件已存在）
    sha = get_file_sha(path)
    
    # 构建请求
    data = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Python Script"
        },
        method="PUT"
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"[OK] Uploaded: {path}")
            return True
    except Exception as e:
        print(f"[FAIL] Upload error: {e}")
        return False

def main():
    print("=" * 50)
    print(" 桐城中学叶老师教学 - Website Update Tool")
    print("=" * 50)
    print()
    
    # 1. Read config
    print("[1] Reading config file...")
    try:
        config = read_config()
        print(f"    Found {len(config['homework_items'])} homework items")
        print(f"    Found {len(config['answers'])} answers")
    except Exception as e:
        print(f"[FAIL] Config read error: {e}")
        input("\nPress Enter to exit...")
        return
    print()
    
    # 2. Generate HTML
    print("[2] Generating webpage...")
    html = generate_html(config)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"    Saved to: {INDEX_FILE}")
    print()
    
    # 3. Upload to GitHub
    print("[3] Uploading to GitHub...")
    success = upload_to_github(html, INDEX_FILE, "Update teaching website content")
    print()
    
    if success:
        print("=" * 50)
        print(" [SUCCESS] Website Updated!")
        print("    https://wisdon470.github.io/wuli/")
        print("=" * 50)
    else:
        print("[FAIL] Upload failed, please check network")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
