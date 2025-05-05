import http.server
import socketserver
import os
import webbrowser
import argparse
import threading
import time

def start_server(port=8000, directory="網頁講義"):
    """啟動一個HTTP服務器來顯示講義內容"""
    # 確保目錄存在
    if not os.path.exists(directory):
        print(f"錯誤: 目錄 '{directory}' 不存在。請先運行 json_to_html.py 生成HTML文件。")
        return
    
    # 切換到網頁講義目錄
    os.chdir(directory)
    
    # 設置服務器
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        # 創建服務器
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"服務器啟動在 http://localhost:{port}")
            print("在瀏覽器中訪問上面的網址查看講義")
            print("按 Ctrl+C 停止服務器")
            
            # 在瀏覽器中自動打開網頁
            webbrowser.open(f"http://localhost:{port}/index.html")
            
            # 運行服務器
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\n服務器已停止")
    except OSError as e:
        if e.errno == 48:  # 地址已被使用
            print(f"錯誤: 端口 {port} 已被使用。請嘗試其他端口。")
        else:
            print(f"錯誤: {e}")

def check_and_generate_html():
    """檢查是否已生成HTML文件，如果沒有則生成"""
    html_dir = "網頁講義"
    lecture_dir = "講義"
    
    if not os.path.exists(html_dir) or not os.path.exists(os.path.join(html_dir, "index.html")):
        print("HTML講義文件不存在，正在生成...")
        
        # 確保講義目錄存在
        if not os.path.exists(lecture_dir):
            print(f"錯誤: 講義目錄 '{lecture_dir}' 不存在。請先生成講義內容。")
            return False
        
        # 運行json_to_html.py生成HTML文件
        import json_to_html
        json_to_html.convert_all_json_files()
        
        # 檢查index.html是否存在
        if not os.path.exists(os.path.join(html_dir, "index.html")):
            print("警告: 索引頁面不存在，可能需要手動創建。")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="啟動一個HTTP服務器來顯示統計學講義")
    parser.add_argument("--port", type=int, default=8000, help="指定服務器端口 (默認: 8000)")
    parser.add_argument("--dir", type=str, default="網頁講義", help="指定網頁目錄 (默認: 網頁講義)")
    
    args = parser.parse_args()
    
    # 檢查並生成HTML文件
    if check_and_generate_html():
        # 啟動服務器
        start_server(args.port, args.dir) 