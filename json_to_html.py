import os
import json
import argparse
import re
import shutil
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import numpy as np
import io
import base64
import platform
from datetime import datetime

# 根據不同操作系統設定適合的中文字型
def set_chinese_font():
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # macOS 系統字型路徑
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/Library/Fonts/Arial Unicode.ttf'
        ]
    elif system == 'Windows':
        # Windows 系統字型路徑
        font_paths = [
            'C:\\Windows\\Fonts\\msyh.ttc',  # 微軟雅黑
            'C:\\Windows\\Fonts\\simsun.ttc',  # 宋體
            'C:\\Windows\\Fonts\\simhei.ttf'   # 黑體
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc'
        ]
    
    # 嘗試每個字型路徑
    for font_path in font_paths:
        if os.path.exists(font_path):
            prop = FontProperties(fname=font_path)
            matplotlib.rcParams['axes.unicode_minus'] = False  # 讓負號正確顯示
            return prop
    
    # 如果找不到特定字型，嘗試通用名稱
    font_names = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'sans-serif']
    for font_name in font_names:
        try:
            prop = FontProperties(family=font_name)
            matplotlib.rcParams['axes.unicode_minus'] = False
            return prop
        except:
            continue
    
    # 如果還是找不到，使用默認設置
    matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'sans-serif']
    matplotlib.rcParams['axes.unicode_minus'] = False
    return None

# 設定中文字型
chinese_font = set_chinese_font()

def convert_section_to_html(section):
    """將小節內容轉換為HTML"""
    html = f'<section id="section-{section["sectionNumber"]}">\n'
    html += f'  <h3>{section["sectionNumber"]} {section["sectionTitle"]}</h3>\n'
    
    # 主要內容
    html += '  <div class="content">\n'
    paragraphs = section["content"].split('\n\n')
    for p in paragraphs:
        if p.strip():
            html += f'    <p>{p.strip()}</p>\n'
    html += '  </div>\n'
    
    # 實際應用例子
    if section.get("examples"):
        html += '  <div class="examples">\n'
        html += '    <h4>實際應用例子</h4>\n'
        html += '    <ul>\n'
        for example in section["examples"]:
            html += f'      <li>{example}</li>\n'
        html += '    </ul>\n'
        html += '  </div>\n'
    
    # 視覺化元素
    if section.get("visuals"):
        html += '  <div class="visuals">\n'
        html += '    <h4>視覺化輔助</h4>\n'
        for visual in section["visuals"]:
            html += f'    <figure>\n'
            html += f'      <img src="{visual["path"]}" alt="{visual["description"]}">\n'
            html += f'      <figcaption>{visual["description"]}</figcaption>\n'
            html += '    </figure>\n'
        html += '  </div>\n'
    
    # 記憶技巧
    if section.get("mnemonics"):
        html += '  <div class="mnemonics">\n'
        html += '    <h4>記憶技巧</h4>\n'
        html += '    <ul>\n'
        for mnemonic in section["mnemonics"]:
            html += f'      <li>{mnemonic}</li>\n'
        html += '    </ul>\n'
        html += '  </div>\n'
    
    # 練習題
    if section.get("exercises"):
        html += '  <div class="exercises">\n'
        html += '    <h4>練習題</h4>\n'
        for i, exercise in enumerate(section["exercises"]):
            html += f'    <div class="exercise">\n'
            html += f'      <p class="question"><strong>問題 {i+1}:</strong> {exercise["question"]}</p>\n'
            html += f'      <p class="answer"><strong>答案:</strong> <span class="hidden-answer">{exercise["answer"]}</span></p>\n'
            html += '    </div>\n'
        html += '  </div>\n'
    
    html += '</section>\n'
    return html

def convert_chapter_to_html(chapter):
    """將章節內容轉換為HTML"""
    html = f'<div class="chapter" id="chapter-{chapter["chapterNumber"]}">\n'
    html += f'  <h2>第{chapter["chapterNumber"]}章：{chapter["chapterTitle"]}</h2>\n'
    
    # 章節概述
    if "overview" in chapter:
        html += '  <div class="overview">\n'
        html += f'    <p>{chapter["overview"]}</p>\n'
        html += '  </div>\n'
    
    # 各小節內容
    for section in chapter["sections"]:
        html += convert_section_to_html(section)
    
    html += '</div>\n'
    return html

def generate_visualization(section_title, section_number):
    """
    為指定的小節生成視覺化內容
    
    參數:
        section_title (str): 小節標題
        section_number (str): 小節編號
    
    返回:
        str: HTML格式的視覺化內容
    """
    chapter_num = section_number.split('.')[0]
    
    # 用於存儲生成的圖片的base64編碼
    visualizations = []
    
    # 第1章：統計學簡介與基本概念
    if chapter_num == '1':
        if section_number == '1.1':  # 統計學的定義與範疇
            # 統計學定義與範疇示意圖
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 建立統計學的主要分類
            main_areas = ['描述統計', '推論統計']
            applications = ['社會科學', '自然科學', '商業', '醫學', '教育']
            
            # 畫主要框架
            ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, fill=True, alpha=0.3, color='lightblue'))
            ax.text(0.5, 0.75, '統計學', ha='center', va='center', fontsize=16, fontweight='bold', fontproperties=chinese_font)
            
            # 畫分支
            ax.add_patch(plt.Rectangle((0.2, 0.4), 0.2, 0.15, fill=True, alpha=0.3, color='lightgreen'))
            ax.add_patch(plt.Rectangle((0.6, 0.4), 0.2, 0.15, fill=True, alpha=0.3, color='lightgreen'))
            
            # 添加文字
            ax.text(0.3, 0.475, main_areas[0], ha='center', va='center', fontsize=12, fontproperties=chinese_font)
            ax.text(0.7, 0.475, main_areas[1], ha='center', va='center', fontsize=12, fontproperties=chinese_font)
            
            # 畫連接線
            ax.plot([0.3, 0.3], [0.6, 0.55], 'k-')
            ax.plot([0.7, 0.7], [0.6, 0.55], 'k-')
            
            # 畫應用領域
            y_pos = 0.2
            for i, app in enumerate(applications):
                x_pos = 0.2 + i * 0.15
                ax.add_patch(plt.Rectangle((x_pos, y_pos-0.05), 0.12, 0.1, fill=True, alpha=0.3, color='lightyellow'))
                ax.text(x_pos+0.06, y_pos, app, ha='center', va='center', fontsize=9, fontproperties=chinese_font)
                
                # 連接到最近的分支
                if i < 2:
                    ax.plot([0.3, x_pos+0.06], [0.4, y_pos+0.05], 'k-', alpha=0.5)
                else:
                    ax.plot([0.7, x_pos+0.06], [0.4, y_pos+0.05], 'k-', alpha=0.5)
            
            # 設置圖表
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 將圖像轉換為base64字符串
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            visualizations.append(f'''
            <div class="visualization-block">
                <h4>統計學的定義與範疇</h4>
                <img src="data:image/png;base64,{img_str}" alt="統計學的定義與範疇" class="img-fluid">
                <p class="text-center text-muted">圖：統計學的主要分支與應用領域</p>
            </div>
            ''')
            
        elif section_number == '1.2':  # 母體與樣本
            # 母體與樣本關係圖
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 繪製母體
            population_circle = plt.Circle((0.5, 0.5), 0.4, fill=True, alpha=0.3, color='lightblue')
            ax.add_patch(population_circle)
            ax.text(0.5, 0.8, '母體 (Population)', ha='center', va='center', fontsize=14, fontproperties=chinese_font)
            
            # 繪製樣本
            for i in range(3):
                sample_circle = plt.Circle((0.3+i*0.2, 0.4), 0.1, fill=True, alpha=0.7, color='lightgreen')
                ax.add_patch(sample_circle)
                ax.text(0.3+i*0.2, 0.4, f'樣本{i+1}', ha='center', va='center', fontsize=10, fontproperties=chinese_font)
            
            # 繪製箭頭
            ax.annotate('', xy=(0.3, 0.25), xytext=(0.3, 0.4-0.1), 
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
            ax.annotate('', xy=(0.5, 0.25), xytext=(0.5, 0.4-0.1), 
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
            ax.annotate('', xy=(0.7, 0.25), xytext=(0.7, 0.4-0.1), 
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
            
            # 添加說明文字
            ax.text(0.5, 0.2, '透過抽樣獲取數據', ha='center', va='center', fontsize=12, fontproperties=chinese_font)
            ax.text(0.3, 0.1, '統計量 (Statistics)', ha='center', va='center', fontsize=10, fontproperties=chinese_font)
            ax.text(0.7, 0.1, '參數 (Parameters)', ha='center', va='center', fontsize=10, fontproperties=chinese_font)
            
            # 設置圖表
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 將圖像轉換為base64字符串
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            visualizations.append(f'''
            <div class="visualization-block">
                <h4>母體與樣本關係圖</h4>
                <img src="data:image/png;base64,{img_str}" alt="母體與樣本關係" class="img-fluid">
                <p class="text-center text-muted">圖：母體與樣本的關係示意圖</p>
            </div>
            ''')
        
        # 為其他小節添加視覺化
        elif section_number == '1.3':  # 資料類型與測量尺度
            # 四種測量尺度比較圖
            fig, ax = plt.subplots(figsize=(10, 6))
            
            scales = ['名目尺度\n(Nominal)', '順序尺度\n(Ordinal)', '區間尺度\n(Interval)', '比率尺度\n(Ratio)']
            examples = ['性別、血型', '排名、等級', '溫度(°C)、智商', '身高、重量']
            operations = ['相等/不相等', '大於/小於', '加法/減法', '乘法/除法']
            
            # 畫表格
            for i in range(4):
                # 尺度名稱
                ax.add_patch(plt.Rectangle((0.1, 0.8-i*0.2), 0.2, 0.15, fill=True, alpha=0.3, color='lightblue'))
                ax.text(0.2, 0.875-i*0.2, scales[i], ha='center', va='center', fontsize=10, fontproperties=chinese_font)
                
                # 例子
                ax.add_patch(plt.Rectangle((0.3, 0.8-i*0.2), 0.3, 0.15, fill=True, alpha=0.3, color='lightgreen'))
                ax.text(0.45, 0.875-i*0.2, examples[i], ha='center', va='center', fontsize=10, fontproperties=chinese_font)
                
                # 可進行的運算
                ax.add_patch(plt.Rectangle((0.6, 0.8-i*0.2), 0.3, 0.15, fill=True, alpha=0.3, color='lightyellow'))
                ax.text(0.75, 0.875-i*0.2, operations[i], ha='center', va='center', fontsize=10, fontproperties=chinese_font)
            
            # 表格標題
            ax.text(0.2, 0.95, '測量尺度', ha='center', va='center', fontsize=12, fontweight='bold', fontproperties=chinese_font)
            ax.text(0.45, 0.95, '例子', ha='center', va='center', fontsize=12, fontweight='bold', fontproperties=chinese_font)
            ax.text(0.75, 0.95, '允許運算', ha='center', va='center', fontsize=12, fontweight='bold', fontproperties=chinese_font)
            
            # 增加信息量
            ax.add_patch(plt.Rectangle((0.1, 0.05), 0.8, 0.15, fill=True, alpha=0.2, color='lightgray'))
            ax.text(0.5, 0.125, '測量尺度由低到高：信息量逐漸增加，允許的數學運算逐漸增多', 
                   ha='center', va='center', fontsize=10, style='italic', fontproperties=chinese_font)
            
            # 設置圖表
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 將圖像轉換為base64字符串
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            visualizations.append(f'''
            <div class="visualization-block">
                <h4>測量尺度比較</h4>
                <img src="data:image/png;base64,{img_str}" alt="測量尺度比較" class="img-fluid">
                <p class="text-center text-muted">圖：四種測量尺度的比較與應用</p>
            </div>
            ''')
            
    # 第2章：資料的收集與呈現
    elif chapter_num == '2':
        if section_number == '2.1':  # 抽樣方法與技巧
            # 不同抽樣方法示意圖
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))
            
            # 簡單隨機抽樣
            population = np.random.rand(100, 2)
            sample_indices = np.random.choice(range(100), 10, replace=False)
            sample = population[sample_indices]
            
            ax1.scatter(population[:, 0], population[:, 1], color='blue', alpha=0.5, s=30)
            ax1.scatter(sample[:, 0], sample[:, 1], color='red', s=50)
            ax1.set_title('簡單隨機抽樣', fontproperties=chinese_font)
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
            ax1.set_xticks([])
            ax1.set_yticks([])
            
            # 分層抽樣
            group1 = np.random.rand(50, 2) * 0.4 + 0.1
            group2 = np.random.rand(50, 2) * 0.4 + [0.5, 0.1]
            
            sample1 = group1[np.random.choice(range(50), 5, replace=False)]
            sample2 = group2[np.random.choice(range(50), 5, replace=False)]
            
            ax2.scatter(group1[:, 0], group1[:, 1], color='blue', alpha=0.5, s=30)
            ax2.scatter(group2[:, 0], group2[:, 1], color='green', alpha=0.5, s=30)
            ax2.scatter(sample1[:, 0], sample1[:, 1], color='red', s=50)
            ax2.scatter(sample2[:, 0], sample2[:, 1], color='red', s=50)
            ax2.set_title('分層抽樣', fontproperties=chinese_font)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.set_xticks([])
            ax2.set_yticks([])
            
            # 系統抽樣
            x = np.linspace(0, 1, 10)
            y = np.ones(10) * 0.5
            systematic_sample = np.column_stack((x, y + np.random.normal(0, 0.05, 10)))
            
            all_points = np.vstack([np.column_stack((xi + np.random.normal(0, 0.03, 10), 
                                                      np.linspace(0, 1, 10) + np.random.normal(0, 0.03, 10))) 
                                     for xi in x])
            
            ax3.scatter(all_points[:, 0], all_points[:, 1], color='blue', alpha=0.5, s=30)
            ax3.scatter(systematic_sample[:, 0], systematic_sample[:, 1], color='red', s=50)
            ax3.set_title('系統抽樣', fontproperties=chinese_font)
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
            ax3.set_xticks([])
            ax3.set_yticks([])
            
            # 叢集抽樣
            clusters = []
            samples = []
            centers = [[0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]
            
            for i, center in enumerate(centers):
                cluster = np.random.normal(0, 0.1, (20, 2)) + center
                clusters.append(cluster)
                
                if i == 1 or i == 2:  # 只從其中兩個叢集抽樣
                    samples.append(cluster)
            
            clusters = np.vstack(clusters)
            samples = np.vstack(samples)
            
            ax4.scatter(clusters[:, 0], clusters[:, 1], color='blue', alpha=0.5, s=30)
            ax4.scatter(samples[:, 0], samples[:, 1], color='red', s=30)
            ax4.plot([0.5, 0.5], [0, 1], 'k--', alpha=0.3)
            ax4.plot([0, 1], [0.5, 0.5], 'k--', alpha=0.3)
            ax4.set_title('叢集抽樣', fontproperties=chinese_font)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.set_xticks([])
            ax4.set_yticks([])
            
            plt.tight_layout()
            
            # 將圖像轉換為base64字符串
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            visualizations.append(f'''
            <div class="visualization-block">
                <h4>抽樣方法比較</h4>
                <img src="data:image/png;base64,{img_str}" alt="抽樣方法比較" class="img-fluid">
                <p class="text-center text-muted">圖：四種常見抽樣方法的示意圖</p>
            </div>
            ''')
    
    # 為其他章節添加視覺化...
    
    # 返回視覺化HTML
    if visualizations:
        return '\n'.join(visualizations)
    else:
        return f'''
        <div class="visualization-placeholder">
            <p class="text-center text-muted">暫無此小節的視覺化輔助</p>
        </div>
        '''

def convert_json_to_html(json_file, output_html=None):
    """
    將JSON格式的講義文件轉換為HTML格式
    
    參數:
        json_file (str): JSON文件路徑
        output_html (str): 輸出HTML文件路徑，默認為與JSON同名的HTML
    
    返回:
        str: 生成的HTML文件路徑
    """
    # 如果未指定輸出文件名，則根據輸入文件名生成
    if output_html is None:
        output_html = os.path.splitext(json_file)[0] + '.html'
    
    # 讀取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 創建HTML頭部
    html = '''<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>統計學講義</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: "Microsoft JhengHei", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        h2 {
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin-top: 30px;
            border-left: 5px solid #3498db;
        }
        h3 {
            color: #34495e;
            margin-top: 25px;
            padding: 8px 0;
            border-bottom: 1px solid #bdc3c7;
        }
        .chapter-title {
            font-size: 24px;
            font-weight: bold;
        }
        .section-content {
            margin-bottom: 20px;
        }
        .examples, .mnemonics, .exercises {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .examples {
            background-color: #e8f4fc;
            border-left: 5px solid #3498db;
        }
        .mnemonics {
            background-color: #fcf3cf;
            border-left: 5px solid #f1c40f;
        }
        .exercises {
            background-color: #e8f8f5;
            border-left: 5px solid #2ecc71;
        }
        .visualization-block {
            background-color: #f0f4f8;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        .visualization-block img {
            max-width: 100%;
            height: auto;
            margin: 10px auto;
        }
        .visualization-placeholder {
            background-color: #f0f4f8;
            border: 1px dashed #d0d7de;
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            color: #7f8c8d;
        }
        .exercise {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #ccc;
        }
        .question {
            font-weight: bold;
        }
        .answer {
            margin-top: 10px;
            padding-left: 20px;
        }
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #e9ecef;
        }
        .toc h2 {
            background: none;
            border-left: none;
            margin-top: 0;
            padding-left: 0;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin-bottom: 5px;
        }
        .toc a {
            text-decoration: none;
            color: #3498db;
        }
        .toc .section-link {
            padding-left: 20px;
            font-size: 0.9em;
        }
        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #3498db;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            text-align: center;
            line-height: 40px;
            text-decoration: none;
            opacity: 0.7;
            transition: opacity 0.3s;
        }
        .back-to-top:hover {
            opacity: 1;
            color: white;
        }
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            .toc {
                padding: 10px;
            }
        }
        .formula {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Cambria Math', Georgia, serif;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <a href="#top" class="back-to-top" title="回到頂部">↑</a>
    <div class="container" id="top">
'''
    
    # 添加課程標題
    html += f'<h1>{data.get("courseTitle", "統計學講義")}</h1>\n'
    
    # 處理章節內容
    if "chapters" in data:
        # 添加目錄
        html += '<div class="toc">\n<h2>目錄</h2>\n<ul>\n'
        
    for chapter in data["chapters"]:
            html += f'<li><a href="#chapter-{chapter["chapterNumber"]}">'
            html += f'第{chapter["chapterNumber"]}章: {chapter["chapterTitle"]}</a>\n<ul>\n'
            
        for section in chapter["sections"]:
                html += f'<li class="section-link"><a href="#section-{section["sectionNumber"]}">'
                html += f'{section["sectionNumber"]} {section["sectionTitle"]}</a></li>\n'
            
            html += '</ul></li>\n'
        
        html += '</ul>\n</div>\n'
        
        # 添加章節內容
    for chapter in data["chapters"]:
            html += f'<h2 id="chapter-{chapter["chapterNumber"]}" class="chapter-title">'
            html += f'第{chapter["chapterNumber"]}章: {chapter["chapterTitle"]}</h2>\n'
            
            if "overview" in chapter:
                html += f'<div class="chapter-overview mb-4">{chapter["overview"]}</div>\n'
            
            # 添加小節內容
            for section in chapter["sections"]:
                html += f'<h3 id="section-{section["sectionNumber"]}">{section["sectionNumber"]} {section["sectionTitle"]}</h3>\n'
                
                # 添加視覺化內容
                visual_content = generate_visualization(section["sectionTitle"], section["sectionNumber"])
                html += f'<div class="visualization-section">\n{visual_content}\n</div>\n'
                
                # 添加小節內容
                if "content" in section:
                    content = section["content"]
                    # 將換行符轉換為HTML段落
                    content = re.sub(r'\n\n+', '</p><p>', content)
                    content = f'<p>{content}</p>'
                    
                    # 替換所有的數學公式標記
                    content = content.replace('$$', '$')
                    
                    html += f'<div class="section-content">\n{content}\n</div>\n'
                
                # 添加例子
                if "examples" in section and section["examples"]:
                    html += '<div class="examples">\n<h4>實際應用例子</h4>\n<ul>\n'
                    for example in section["examples"]:
                        html += f'<li>{example}</li>\n'
                    html += '</ul>\n</div>\n'
                
                # 添加記憶技巧
                if "mnemonics" in section and section["mnemonics"]:
                    html += '<div class="mnemonics">\n<h4>記憶技巧</h4>\n<ul>\n'
                    for mnemonic in section["mnemonics"]:
                        html += f'<li>{mnemonic}</li>\n'
                    html += '</ul>\n</div>\n'
                
                # 添加練習題
                if "exercises" in section and section["exercises"]:
                    html += '<div class="exercises">\n<h4>練習題</h4>\n'
                    for i, exercise in enumerate(section["exercises"]):
                        html += f'<div class="exercise">\n'
                        html += f'<div class="question">問題{i+1}: {exercise["question"]}</div>\n'
                        html += f'<div class="answer">答案: {exercise["answer"]}</div>\n'
                        html += '</div>\n'
                    html += '</div>\n'
    
    # 添加HTML尾部
    html += '''    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        MathJax = {
            tex: {
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']]
            }
        };
        
        // 添加平滑滾動
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // 添加回到頂部按鈕顯示/隱藏功能
        window.addEventListener('scroll', function() {
            var backToTop = document.querySelector('.back-to-top');
            if (window.pageYOffset > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });
    </script>
</body>
</html>'''
    
    # 寫入HTML文件
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"轉換 {json_file} 為 {output_html}...")
    
    return output_html

def convert_all_json_files():
    """轉換講義目錄中的所有JSON文件"""
    lecture_dir = "講義"
    html_dir = "網頁講義"
    
    # 確保輸出目錄存在
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
    
    # 處理個別章節文件
    for filename in os.listdir(lecture_dir):
        if filename.endswith('.json') and '完整' in filename:
            json_path = os.path.join(lecture_dir, filename)
            html_filename = filename.replace('.json', '.html')
            html_path = os.path.join(html_dir, html_filename)
            
            print(f"轉換 {json_path} 為 {html_path}...")
            convert_json_to_html(json_path, html_path)
    
    # 處理完整講義文件
    combined_json = os.path.join(lecture_dir, "統計學完整講義.json")
    if os.path.exists(combined_json):
        combined_html = os.path.join(html_dir, "統計學完整講義.html")
        print(f"轉換完整講義為 {combined_html}...")
        convert_json_to_html(combined_json, combined_html)
    
    print(f"所有HTML文件已生成至: {html_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將JSON講義轉換為HTML網頁")
    parser.add_argument('--all', action='store_true', help='轉換所有JSON文件')
    parser.add_argument('--file', type=str, help='指定要轉換的JSON文件')
    parser.add_argument('--output', type=str, help='指定輸出的HTML文件')
    
    args = parser.parse_args()
    
    if args.all:
        convert_all_json_files()
    elif args.file:
        output_file = args.output if args.output else None
        convert_json_to_html(args.file, output_file)
        print(f"已轉換 {args.file} 至 {output_file or os.path.splitext(args.file)[0] + '.html'}")
    else:
        parser.print_help() 