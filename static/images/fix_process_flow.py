#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import platform

def setup_chinese_font():
    """設置適合當前系統的中文字體"""
    system = platform.system()
    if system == 'Darwin':  # macOS
        # 嘗試幾種可能的macOS中文字體
        fonts = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/Hiragino Sans GB.ttc'
        ]
    elif system == 'Windows':
        fonts = [
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/STKAITI.TTF'
        ]
    else:  # Linux或其它
        fonts = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc'
        ]
    
    # 尋找第一個存在的字體
    chinese_font = None
    for font in fonts:
        if os.path.exists(font):
            chinese_font = font
            break
    
    if chinese_font:
        print(f"找到中文字體: {chinese_font}")
        # 注冊字體文件
        font_prop = fm.FontProperties(fname=chinese_font)
        return font_prop
    else:
        print("警告：沒有找到可用的中文字體！將嘗試使用系統默認字體。")
        return None

def update_process_flow_chart(font_prop=None):
    """更新統計流程圖，確保中文顯示正確"""
    # 創建圖形
    plt.figure(figsize=(12, 8))
    
    # 設定顏色
    bg_color = '#f8f9fa'
    box_colors = ['#c6e2ff', '#ffddc6', '#c6ffe2', '#f2ffc6']
    arrow_color = '#343a40'
    
    # 設定畫布底色
    plt.gca().set_facecolor(bg_color)
    
    # 定義流程步驟和位置
    steps = ['資料收集', '資料整理', '資料分析', '統計推論']
    positions = [(0.2, 0.7), (0.5, 0.7), (0.8, 0.7), (0.5, 0.3)]
    
    # 連接線路徑 (從哪一步到哪一步)
    connections = [(0, 1), (1, 2), (2, 3)]
    
    # 設定標題
    title = '統計學的研究流程'
    if font_prop:
        plt.title(title, fontsize=20, fontweight='bold', pad=20, fontproperties=font_prop)
    else:
        plt.title(title, fontsize=20, fontweight='bold', pad=20)
    
    # 繪製方框和文字
    boxes = []
    for i, (step, pos) in enumerate(zip(steps, positions)):
        # 繪製方框
        box = plt.Rectangle((pos[0]-0.15, pos[1]-0.10), 0.30, 0.20, 
                          facecolor=box_colors[i], edgecolor='black', 
                          alpha=0.9, zorder=1, linewidth=2)
        plt.gca().add_patch(box)
        boxes.append(box)
        
        # 添加文字
        if font_prop:
            plt.text(pos[0], pos[1], step, ha='center', va='center', 
                   fontsize=16, fontweight='bold', fontproperties=font_prop,
                   bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.2'))
        else:
            plt.text(pos[0], pos[1], step, ha='center', va='center', 
                   fontsize=16, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.2'))
    
    # 繪製連接箭頭
    for start, end in connections:
        start_pos = positions[start]
        end_pos = positions[end]
        
        # 計算箭頭方向
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # 繪製箭頭
        plt.arrow(start_pos[0]+0.15, start_pos[1], dx-0.30, dy, 
                head_width=0.04, head_length=0.04, fc=arrow_color, ec=arrow_color, 
                linewidth=2, zorder=2)
    
    # 添加特殊連接：從資料分析到統計推論（向下）
    plt.arrow(positions[2][0], positions[2][1]-0.10, 0, -0.20, 
             head_width=0.04, head_length=0.04, fc=arrow_color, ec=arrow_color, 
             linewidth=2, zorder=2)
    
    # 添加解釋性文字說明
    explanations = [
        '設計調查問卷\n選擇適當的抽樣方法\n收集原始數據',
        '數據清理與轉換\n整理成方便分析的形式\n製作統計圖表',
        '計算統計量\n如平均數、標準差\n探索數據模式',
        '針對母體參數進行估計\n檢定統計假設\n應用統計模型'
    ]
    
    # 添加每個步驟的解釋
    for i, (pos, explanation) in enumerate(zip(positions, explanations)):
        offset_y = -0.20 if i < 3 else 0.25
        offset_x = 0
        
        if font_prop:
            plt.text(pos[0]+offset_x, pos[1]+offset_y, explanation, 
                   ha='center', va='center', fontsize=10, 
                   fontproperties=font_prop,
                   bbox=dict(facecolor='white', alpha=0.7, 
                           boxstyle='round,pad=0.5', edgecolor=box_colors[i]))
        else:
            plt.text(pos[0]+offset_x, pos[1]+offset_y, explanation, 
                   ha='center', va='center', fontsize=10,
                   bbox=dict(facecolor='white', alpha=0.7, 
                           boxstyle='round,pad=0.5', edgecolor=box_colors[i]))
    
    # 添加整體流程循環箭頭（從統計推論回到資料收集）
    plt.annotate('', xy=(0.2, 0.55), xytext=(0.5, 0.25),
                arrowprops=dict(facecolor=arrow_color, shrink=0.05, width=1.5,
                              headwidth=8, headlength=10, connectionstyle='arc3,rad=-0.3'))
    
    # 添加循環說明
    cycle_explanation = '基於推論結果設計新調查，持續優化研究過程'
    if font_prop:
        plt.text(0.28, 0.42, cycle_explanation, 
               ha='center', va='center', fontsize=10, color='#555555',
               fontproperties=font_prop,
               rotation=-15, style='italic')
    else:
        plt.text(0.28, 0.42, cycle_explanation, 
               ha='center', va='center', fontsize=10, color='#555555',
               rotation=-15, style='italic')
    
    # 關閉座標軸
    plt.axis('off')
    
    # 設定視圖範圍
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    
    # 保存圖片
    os.makedirs('ch1', exist_ok=True)
    plt.savefig('ch1/process_flow.png', dpi=120, bbox_inches='tight', facecolor=bg_color)
    print(f"已生成統計流程圖：{os.path.abspath('ch1/process_flow.png')}")
    
    plt.close()

if __name__ == "__main__":
    print("更新統計流程圖...")
    print(f"當前運行環境: {platform.system()} {platform.release()}")
    
    # 設置中文字體
    font_prop = setup_chinese_font()
    
    # 更新統計流程圖
    update_process_flow_chart(font_prop) 