#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
import numpy as np

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
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/Apple Color Emoji.ttc'
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
        plt.rcParams['font.family'] = font_prop.get_name()
        return font_prop
    else:
        print("警告：沒有找到可用的中文字體！將嘗試使用系統默認字體。")
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
        return None

# 測試文字顯示
def test_font_display(font_prop=None):
    """測試中文字體顯示"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 設置背景顏色
    ax.set_facecolor('#f5f5f5')
    
    # 標題與文字
    title = "中文字體顯示測試"
    if font_prop:
        ax.set_title(title, fontproperties=font_prop, fontsize=20)
    else:
        ax.set_title(title, fontsize=20)
    
    # 顯示一些測試文字
    test_texts = [
        "統計學四大流程：資料收集 → 資料整理 → 資料分析 → 統計推論",
        "母體 (Population) 與樣本 (Sample) 的關係",
        "長條圖與圓餅圖是常用的類別資料視覺化方法",
        "常見的圖表扭曲技巧：Y軸截斷、不恰當的圖表類型"
    ]
    
    y_positions = [0.8, 0.6, 0.4, 0.2]
    
    for text, y in zip(test_texts, y_positions):
        if font_prop:
            ax.text(0.5, y, text, ha='center', va='center', fontproperties=font_prop, 
                  fontsize=14, bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='blue', alpha=0.7))
        else:
            ax.text(0.5, y, text, ha='center', va='center', 
                  fontsize=14, bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='blue', alpha=0.7))
    
    # 移除軸線和刻度
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    
    # 保存測試圖片
    plt.savefig('chinese_test.png', dpi=120, bbox_inches='tight')
    print(f"已生成測試圖片：{os.path.abspath('chinese_test.png')}")
    
    plt.close()

def update_process_flow_chart(font_prop=None):
    """更新統計學流程圖，確保中文顯示正確"""
    fig, ax = plt.subplots(figsize=(10, 5))
    steps = ['資料收集', '資料整理', '資料分析', '統計推論']
    x = np.arange(len(steps))
    ax.plot(x, [1, 1, 1, 1], 'bo-', linewidth=2, markersize=12)

    # 繪製步驟說明框
    for i, (step, xi) in enumerate(zip(steps, x)):
        if font_prop:
            ax.text(xi, 1.2, step, ha='center', va='center', fontsize=14, fontproperties=font_prop,
                bbox=dict(boxstyle='round,pad=0.5', fc='skyblue', ec='blue', alpha=0.7))
        else:
            ax.text(xi, 1.2, step, ha='center', va='center', fontsize=14,
                bbox=dict(boxstyle='round,pad=0.5', fc='skyblue', ec='blue', alpha=0.7))
        
        # 為每個步驟添加簡短說明
        descriptions = [
            '透過抽樣、實驗\n或既有資料庫\n取得數據',
            '對原始數據進行\n分類、編碼和\n清理',
            '應用統計方法\n計算、檢定\n與圖表呈現',
            '根據樣本數據\n對母體推論\n做出決策'
        ]
        if font_prop:
            ax.text(xi, 0.7, descriptions[i], ha='center', va='center', fontsize=10, fontproperties=font_prop,
                bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='lightgray'))
        else:
            ax.text(xi, 0.7, descriptions[i], ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='lightgray'))

    # 添加流程箭頭
    for i in range(len(steps)-1):
        ax.annotate('', xy=(x[i+1]-0.3, 1), xytext=(x[i]+0.3, 1), 
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    if font_prop:
        ax.set_title('統計學四大流程示意圖', fontsize=16, fontproperties=font_prop)
    else:
        ax.set_title('統計學四大流程示意圖', fontsize=16)

    # 調整圖的範圍以適應所有元素
    ax.set_xlim(-0.5, len(steps)-0.5)
    ax.set_ylim(0.5, 1.5)

    # 保存圖片到ch1目錄
    os.makedirs('ch1', exist_ok=True)
    plt.savefig('ch1/process_flow.png', dpi=120, bbox_inches='tight')
    print(f"已生成流程圖：{os.path.abspath('ch1/process_flow.png')}")
    
    plt.close()

if __name__ == "__main__":
    print("測試中文字體顯示...")
    print(f"當前運行環境: {platform.system()} {platform.release()}")
    
    # 設置中文字體
    font_prop = setup_chinese_font()
    
    # 測試字體顯示
    test_font_display(font_prop)
    
    # 更新流程圖
    update_process_flow_chart(font_prop) 