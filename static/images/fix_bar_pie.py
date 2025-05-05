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

def update_bar_pie_chart(font_prop=None):
    """更新條形圖和圓餅圖，確保中文顯示正確"""
    # 創建一個並排的條形圖和圓餅圖
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # 設定標題
    title = '類別資料的整理與呈現'
    if font_prop:
        fig.suptitle(title, fontsize=20, fontweight='bold', fontproperties=font_prop)
    else:
        fig.suptitle(title, fontsize=20, fontweight='bold')
    
    # 數據：假設的學生選課調查結果
    categories = ['資料科學', '人工智能', '網頁開發', '資訊安全', '雲計算']
    values = [38, 25, 30, 20, 15]
    colors = plt.cm.Paired(np.linspace(0.1, 0.9, len(categories)))
    
    # 左側：條形圖
    bars = ax1.bar(categories, values, color=colors)
    
    if font_prop:
        ax1.set_title('學生選課偏好 (條形圖)', fontsize=16, fontproperties=font_prop)
        ax1.set_xlabel('課程類別', fontsize=14, fontproperties=font_prop)
        ax1.set_ylabel('學生數量', fontsize=14, fontproperties=font_prop)
    else:
        ax1.set_title('學生選課偏好 (條形圖)', fontsize=16)
        ax1.set_xlabel('課程類別', fontsize=14)
        ax1.set_ylabel('學生數量', fontsize=14)
    
    # 在條形上方添加數值標籤
    for bar in bars:
        height = bar.get_height()
        if font_prop:
            ax1.annotate(f'{height}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3點的垂直偏移
                       textcoords="offset points",
                       ha='center', fontweight='bold', fontproperties=font_prop)
        else:
            ax1.annotate(f'{height}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3點的垂直偏移
                       textcoords="offset points",
                       ha='center', fontweight='bold')
    
    # 添加網格線
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 右側：圓餅圖
    if font_prop:
        # 使用fontproperties處理餅圖標籤
        wedges, texts, autotexts = ax2.pie(values, 
                                         labels=None,  # 先不設置標籤
                                         autopct='%1.1f%%',
                                         startangle=90,
                                         colors=colors,
                                         explode=[0.05, 0, 0, 0, 0])  # 突出第一塊
        
        # 手動設置百分比標籤字體
        for autotext in autotexts:
            autotext.set_fontproperties(font_prop)
            autotext.set_size(10)
            autotext.set_weight('bold')
        
        # 單獨添加類別標籤使用圖例而不是直接在餅圖上標記
        ax2.legend(wedges, categories, 
                  title="課程類別",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  prop=font_prop)  # 使用prop設置圖例字體
        
        ax2.set_title('學生選課偏好 (圓餅圖)', fontsize=16, fontproperties=font_prop)
    else:
        ax2.pie(values, 
              labels=categories,
              autopct='%1.1f%%',
              startangle=90,
              colors=colors,
              explode=[0.05, 0, 0, 0, 0])  # 突出第一塊
        
        ax2.set_title('學生選課偏好 (圓餅圖)', fontsize=16)
    
    ax2.axis('equal')  # 使餅圖為正圓形
    
    # 添加說明文字
    explanation = """
條形圖適用於比較不同類別的數量差異，
而圓餅圖則適合呈現部分與整體的關係。

條形圖優點：
- 直觀比較不同類別的數值大小
- 容易識別最大和最小類別
- 可以有效展示時間變化趨勢

圓餅圖優點：
- 清晰顯示每個類別占總體的比例
- 適合展示構成分析
- 視覺上強調部分與整體的關係
"""
    
    if font_prop:
        plt.figtext(0.5, 0.01, explanation, 
                   ha='center', va='bottom', fontsize=12, fontproperties=font_prop,
                   bbox=dict(boxstyle='round,pad=1', fc='#f8f9fa', ec='#343a40', alpha=0.8))
    else:
        plt.figtext(0.5, 0.01, explanation, 
                   ha='center', va='bottom', fontsize=12,
                   bbox=dict(boxstyle='round,pad=1', fc='#f8f9fa', ec='#343a40', alpha=0.8))
    
    # 調整布局
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    # 保存圖片
    os.makedirs('ch3', exist_ok=True)
    plt.savefig('ch3/bar_pie.png', dpi=120, bbox_inches='tight')
    print(f"已生成條形圖和圓餅圖：{os.path.abspath('ch3/bar_pie.png')}")
    
    plt.close()

if __name__ == "__main__":
    print("更新條形圖和圓餅圖...")
    print(f"當前運行環境: {platform.system()} {platform.release()}")
    
    # 設置中文字體
    font_prop = setup_chinese_font()
    
    # 更新條形圖和圓餅圖
    update_bar_pie_chart(font_prop) 