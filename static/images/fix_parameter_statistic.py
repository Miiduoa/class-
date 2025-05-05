#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import platform
from matplotlib.patches import Circle, FancyArrowPatch, Ellipse

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

def update_parameter_statistic_diagram(font_prop=None):
    """更新母體與樣本關係圖，確保中文顯示正確"""
    # 創建圖形
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # 設定背景色
    bg_color = '#f8f9fa'
    ax.set_facecolor(bg_color)
    fig.set_facecolor(bg_color)
    
    # 顏色設定
    population_color = '#3498db'  # 藍色
    sample_color = '#e74c3c'      # 紅色
    arrow_color = '#2c3e50'       # 深灰藍色
    
    # 關閉座標軸
    ax.axis('off')
    
    # 設定標題
    title = '母體與樣本的關係'
    if font_prop:
        ax.set_title(title, fontsize=22, fontweight='bold', pad=20, fontproperties=font_prop)
    else:
        ax.set_title(title, fontsize=22, fontweight='bold', pad=20)
    
    # 繪製母體圓圈（大圓）
    population_circle = Circle((0.5, 0.6), 0.35, fill=True, 
                             facecolor=population_color, alpha=0.2, 
                             edgecolor=population_color, linewidth=2, zorder=1)
    ax.add_patch(population_circle)
    
    # 繪製樣本圓圈（小圓）
    sample_circle = Circle((0.5, 0.6), 0.15, fill=True, 
                          facecolor=sample_color, alpha=0.4, 
                          edgecolor=sample_color, linewidth=2, zorder=2)
    ax.add_patch(sample_circle)
    
    # 添加母體標籤
    if font_prop:
        ax.text(0.5, 0.95, '母體 (Population)', ha='center', va='center', 
               fontsize=18, fontweight='bold', fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5',
                       edgecolor=population_color, linewidth=2))
    else:
        ax.text(0.5, 0.95, '母體 (Population)', ha='center', va='center', 
               fontsize=18, fontweight='bold',
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5',
                       edgecolor=population_color, linewidth=2))
    
    # 添加樣本標籤
    if font_prop:
        ax.text(0.5, 0.25, '樣本 (Sample)', ha='center', va='center', 
               fontsize=18, fontweight='bold', fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5',
                       edgecolor=sample_color, linewidth=2))
    else:
        ax.text(0.5, 0.25, '樣本 (Sample)', ha='center', va='center', 
               fontsize=18, fontweight='bold',
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5',
                       edgecolor=sample_color, linewidth=2))
    
    # 添加隨機抽樣箭頭（從母體到樣本的過程）
    sampling_arrow = FancyArrowPatch((0.3, 0.35), (0.35, 0.5),
                                   connectionstyle="arc3,rad=-0.3",
                                   arrowstyle="Simple,head_width=10,head_length=10",
                                   linewidth=2, color=arrow_color)
    ax.add_patch(sampling_arrow)
    
    # 添加抽樣標籤
    sampling_label = '隨機抽樣\n(Random Sampling)'
    if font_prop:
        ax.text(0.2, 0.4, sampling_label, ha='center', va='center', 
               fontsize=12, fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    else:
        ax.text(0.2, 0.4, sampling_label, ha='center', va='center', 
               fontsize=12,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    # 添加統計推論箭頭（從樣本到母體的過程）
    inference_arrow = FancyArrowPatch((0.65, 0.5), (0.7, 0.35),
                                    connectionstyle="arc3,rad=-0.3",
                                    arrowstyle="Simple,head_width=10,head_length=10",
                                    linewidth=2, color=arrow_color)
    ax.add_patch(inference_arrow)
    
    # 添加推論標籤
    inference_label = '統計推論\n(Statistical Inference)'
    if font_prop:
        ax.text(0.8, 0.4, inference_label, ha='center', va='center', 
               fontsize=12, fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    else:
        ax.text(0.8, 0.4, inference_label, ha='center', va='center', 
               fontsize=12,
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    # 添加參數與統計量說明
    parameter_text = '母體參數 (Parameters)：\n- μ (母體平均數)\n- σ (母體標準差)\n- N (母體大小)'
    statistic_text = '樣本統計量 (Statistics)：\n- x̄ (樣本平均數)\n- s (樣本標準差)\n- n (樣本大小)'
    
    # 母體參數說明
    if font_prop:
        ax.text(0.15, 0.75, parameter_text, 
               fontsize=12, fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5',
                       edgecolor=population_color))
    else:
        ax.text(0.15, 0.75, parameter_text, 
               fontsize=12,
               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5',
                       edgecolor=population_color))
    
    # 樣本統計量說明
    if font_prop:
        ax.text(0.85, 0.75, statistic_text, 
               fontsize=12, fontproperties=font_prop,
               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5',
                       edgecolor=sample_color))
    else:
        ax.text(0.85, 0.75, statistic_text, 
               fontsize=12,
               bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.5',
                       edgecolor=sample_color))
    
    # 添加底部說明文字
    explanation = """
統計學的核心概念是通過樣本了解母體的特性。
研究者通常無法研究整個母體，所以會抽取有代表性的樣本。
藉由樣本統計量（如平均數、標準差）推斷母體參數，這個過程稱為統計推論。
良好的抽樣方法能增加樣本代表性，提高統計推論的準確性。
"""
    
    if font_prop:
        fig.text(0.5, 0.05, explanation, ha='center', fontsize=12, fontproperties=font_prop,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.8',
                        edgecolor='#bdc3c7'))
    else:
        fig.text(0.5, 0.05, explanation, ha='center', fontsize=12,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.8',
                        edgecolor='#bdc3c7'))
    
    # 模擬一些數據點
    np.random.seed(42)
    num_points = 200
    
    # 母體點 - 藍色小點
    angles = np.random.uniform(0, 2*np.pi, num_points)
    radii = np.random.uniform(0, 0.35, num_points)
    x_pop = 0.5 + radii * np.cos(angles)
    y_pop = 0.6 + radii * np.sin(angles)
    
    # 隨機選擇一些點作為樣本點
    sample_indices = np.random.choice(range(num_points), 25, replace=False)
    
    # 繪製母體點（不是樣本的部分）
    non_sample_indices = [i for i in range(num_points) if i not in sample_indices]
    ax.scatter(x_pop[non_sample_indices], y_pop[non_sample_indices], 
              s=10, alpha=0.5, c=population_color, zorder=0)
    
    # 繪製樣本點 - 紅色小點
    ax.scatter(x_pop[sample_indices], y_pop[sample_indices], 
              s=30, alpha=0.8, c=sample_color, zorder=3, edgecolor='white')
    
    # 設定視圖範圍
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # 保存圖片
    os.makedirs('ch1', exist_ok=True)
    plt.savefig('ch1/parameter_statistic.png', dpi=120, bbox_inches='tight', facecolor=bg_color)
    print(f"已生成母體與樣本關係圖：{os.path.abspath('ch1/parameter_statistic.png')}")
    
    plt.close()

if __name__ == "__main__":
    print("更新母體與樣本關係圖...")
    print(f"當前運行環境: {platform.system()} {platform.release()}")
    
    # 設置中文字體
    font_prop = setup_chinese_font()
    
    # 更新母體與樣本關係圖
    update_parameter_statistic_diagram(font_prop) 