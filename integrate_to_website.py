import os
import json
import shutil
import argparse
import requests
from datetime import datetime
import re
import zipfile

def check_website_api(api_url, api_key=None):
    """
    檢查網站API是否可用
    
    參數:
        api_url (str): API的基礎URL
        api_key (str): API金鑰 (如果需要的話)
    
    返回:
        bool: API是否可用
    """
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    try:
        response = requests.get(f"{api_url}/status", headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"無法連接到網站API: {str(e)}")
        return False

def upload_lecture_to_website(html_dir, api_url, api_key=None, chapter_num=None):
    """
    通過API上傳講義到網站
    
    參數:
        html_dir (str): HTML講義目錄
        api_url (str): API的基礎URL
        api_key (str): API金鑰
        chapter_num (int): 指定上傳的章節編號，None表示上傳所有章節
    """
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    # 檢查HTML目錄是否存在
    if not os.path.exists(html_dir):
        print(f"錯誤: HTML目錄 '{html_dir}' 不存在，請先生成HTML文件。")
        return False
    
    # 獲取要上傳的HTML文件
    html_files = []
    if chapter_num:
        specific_file = os.path.join(html_dir, f"第{chapter_num}章_完整.html")
        if os.path.exists(specific_file):
            html_files.append(specific_file)
        else:
            print(f"錯誤: 指定的章節文件 '{specific_file}' 不存在。")
            return False
    else:
        for filename in os.listdir(html_dir):
            if filename.endswith('.html') and filename != 'index.html':
                html_files.append(os.path.join(html_dir, filename))
    
    if not html_files:
        print(f"錯誤: 在 '{html_dir}' 中沒有找到要上傳的HTML文件。")
        return False
    
    # 上傳每個HTML文件
    success_count = 0
    for html_file in html_files:
        filename = os.path.basename(html_file)
        
        # 解析章節號
        match = re.match(r'第(\d+)章', filename)
        if match:
            chapter_id = int(match.group(1))
        else:
            print(f"警告: 無法從 '{filename}' 中解析章節號，跳過此文件。")
            continue
        
        # 讀取HTML內容
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 提取標題
        title_match = re.search(r'<title>(.*?)</title>', html_content)
        title = title_match.group(1) if title_match else f"統計學第{chapter_id}章"
        
        # 準備上傳數據
        payload = {
            'chapter_id': chapter_id,
            'title': title,
            'content': html_content,
            'is_published': True
        }
        
        try:
            # 發送API請求
            response = requests.post(
                f"{api_url}/lectures",
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                print(f"成功上傳: {filename}")
                success_count += 1
            else:
                print(f"上傳失敗: {filename}, 狀態碼: {response.status_code}, 回應: {response.text}")
        
        except Exception as e:
            print(f"上傳 '{filename}' 時出錯: {str(e)}")
    
    print(f"完成上傳: {success_count}/{len(html_files)} 個文件成功")
    return success_count > 0

def prepare_website_package(html_dir, output_dir="website_package"):
    """
    準備一個包含所有講義HTML文件的網站包
    
    參數:
        html_dir (str): HTML講義目錄
        output_dir (str): 輸出目錄
    """
    if not os.path.exists(html_dir):
        print(f"錯誤: HTML目錄 '{html_dir}' 不存在。")
        return False
    
    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "static", "js"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "static", "images"), exist_ok=True)
    
    # 創建CSS文件
    css_content = """/* 統計學講義樣式 */
body {
    font-family: "Microsoft JhengHei", Arial, sans-serif;
    line-height: 1.6;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
h1, h2, h3, h4 { color: #333; }
h1 { text-align: center; margin-bottom: 30px; }
h2 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 40px; }
h3 { margin-top: 30px; background: #f0f0f0; padding: 10px; }
.content { margin-bottom: 20px; }
.examples, .mnemonics, .exercises, .visuals { 
    background: #f9f9f9; 
    padding: 15px; 
    margin: 20px 0; 
    border-radius: 5px; 
}
.exercise { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #ccc; }
.question { font-weight: bold; }
.answer { color: #555; }
.toc { background: #f0f0f0; padding: 20px; margin-bottom: 30px; border-radius: 5px; }
.toc h2 { border-bottom: none; margin-top: 0; }

/* 響應式樣式 */
@media (max-width: 768px) {
    body { padding: 10px; }
    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.3rem; }
}

/* 打印樣式 */
@media print {
    body { max-width: 100%; }
    .toc { page-break-after: always; }
    h2, h3 { page-break-after: avoid; }
    .examples, .mnemonics, .exercises { page-break-inside: avoid; }
}
"""
    with open(os.path.join(output_dir, "static", "css", "statistics.css"), 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # 創建JS文件
    js_content = """// 統計學講義功能腳本
document.addEventListener('DOMContentLoaded', function() {
    // 添加目錄導航
    buildTableOfContents();
    
    // 添加答案顯示/隱藏功能
    setupAnswerToggle();
});

// 建立目錄
function buildTableOfContents() {
    const toc = document.querySelector('.toc');
    if (!toc) return;
    
    const headings = document.querySelectorAll('h3');
    if (headings.length > 0) {
        const tocList = document.createElement('ul');
        headings.forEach(heading => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `#${heading.id}`;
            a.textContent = heading.textContent;
            li.appendChild(a);
            tocList.appendChild(li);
        });
        toc.appendChild(tocList);
    }
}

// 設置答案切換功能
function setupAnswerToggle() {
    const answers = document.querySelectorAll('.answer');
    answers.forEach(answer => {
        const questionText = answer.previousElementSibling;
        if (questionText && questionText.classList.contains('question')) {
            // 初始隱藏答案
            answer.style.display = 'none';
            
            // 添加切換按鈕
            const toggleBtn = document.createElement('button');
            toggleBtn.textContent = '顯示答案';
            toggleBtn.className = 'toggle-answer';
            toggleBtn.style.marginLeft = '10px';
            toggleBtn.style.padding = '3px 8px';
            toggleBtn.style.background = '#f0f0f0';
            toggleBtn.style.border = '1px solid #ddd';
            toggleBtn.style.borderRadius = '3px';
            toggleBtn.style.cursor = 'pointer';
            
            questionText.appendChild(toggleBtn);
            
            // 綁定點擊事件
            toggleBtn.addEventListener('click', function() {
                if (answer.style.display === 'none') {
                    answer.style.display = 'block';
                    this.textContent = '隱藏答案';
                } else {
                    answer.style.display = 'none';
                    this.textContent = '顯示答案';
                }
            });
        }
    });
}
"""
    with open(os.path.join(output_dir, "static", "js", "statistics.js"), 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 複製HTML文件
    html_count = 0
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            src_file = os.path.join(html_dir, filename)
            dest_file = os.path.join(output_dir, filename)
            
            # 讀取HTML內容
            with open(src_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修改引用路徑
            content = content.replace('</head>', 
                '  <link rel="stylesheet" href="static/css/statistics.css">\n</head>')
            content = content.replace('</body>', 
                '  <script src="static/js/statistics.js"></script>\n</body>')
            
            # 保存修改後的HTML
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            html_count += 1
    
    # 創建一個ZIP包
    zip_filename = f"statistics_website_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    print(f"網站包已創建: {zip_filename}")
    print(f"包含了 {html_count} 個HTML文件和相關的CSS/JS資源")
    
    return zip_filename

def generate_and_prepare_html(json_dir="講義", html_dir="網頁講義"):
    """
    確保所有JSON文件已轉換為HTML
    
    參數:
        json_dir (str): JSON講義目錄
        html_dir (str): HTML講義目錄
    """
    # 檢查並運行json_to_html.py
    import sys
    try:
        import json_to_html
        
        print("正在生成HTML講義文件...")
        json_to_html.convert_all_json_files()
        return True
    except ImportError:
        print("錯誤: 找不到json_to_html模組。請確保該文件在當前目錄中。")
        return False
    except Exception as e:
        print(f"生成HTML時出錯: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將統計學講義整合到網站")
    subparsers = parser.add_subparsers(dest="command", help="操作命令")
    
    # 創建網站包的命令
    package_parser = subparsers.add_parser("package", help="創建網站包")
    package_parser.add_argument("--html-dir", default="網頁講義", help="HTML講義目錄 (默認: 網頁講義)")
    package_parser.add_argument("--output-dir", default="website_package", help="輸出目錄 (默認: website_package)")
    
    # 上傳到網站的命令
    upload_parser = subparsers.add_parser("upload", help="上傳講義到網站")
    upload_parser.add_argument("--html-dir", default="網頁講義", help="HTML講義目錄 (默認: 網頁講義)")
    upload_parser.add_argument("--api-url", required=True, help="網站API的URL")
    upload_parser.add_argument("--api-key", help="API金鑰")
    upload_parser.add_argument("--chapter", type=int, help="指定上傳的章節編號，省略則上傳所有章節")
    
    args = parser.parse_args()
    
    # 首先確保HTML文件已生成
    if not generate_and_prepare_html():
        sys.exit(1)
    
    # 執行相應的命令
    if args.command == "package":
        prepare_website_package(args.html_dir, args.output_dir)
    elif args.command == "upload":
        if check_website_api(args.api_url, args.api_key):
            upload_lecture_to_website(args.html_dir, args.api_url, args.api_key, args.chapter)
        else:
            print("無法連接到網站API，請檢查API URL和金鑰是否正確。")
    else:
        parser.print_help() 