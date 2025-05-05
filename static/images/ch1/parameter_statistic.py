#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import sys

# 嘗試設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'STHeiti', 'Microsoft YaHei', 'SimHei', 'AppleGothic']
plt.rcParams['axes.unicode_minus'] = False

# 第1章 - 母體與樣本關係與統計推論流程
fig, ax = plt.subplots(figsize=(12, 8))

# 創建一個裝飾性背景
ax.add_patch(plt.Rectangle((0, 0), 1, 1, fill=True, color='#f5f5f5'))

# 母體與樣本的視覺化 - 使用更具視覺吸引力的圖形
population_circle = plt.Circle((0.3, 0.7), 0.2, fill=True, alpha=0.7, color='#3498db')
population_points = []
np.random.seed(42)
for _ in range(200):
    r = 0.18 * np.sqrt(np.random.random())
    theta = np.random.random() * 2 * np.pi
    x = 0.3 + r * np.cos(theta)
    y = 0.7 + r * np.sin(theta)
    population_points.append((x, y))

# 樣本是母體的子集
sample_indices = np.random.choice(len(population_points), 30, replace=False)
sample_points = [population_points[i] for i in sample_indices]

# 繪製母體點
for x, y in population_points:
    ax.plot(x, y, 'o', color='#3498db', markersize=3, alpha=0.4)

# 繪製樣本點 - 使用不同顏色並增大
for x, y in sample_points:
    ax.plot(x, y, 'o', color='#e74c3c', markersize=5)

# 母體邊框
population_border = plt.Circle((0.3, 0.7), 0.2, fill=False, color='#2980b9', linewidth=2)
ax.add_patch(population_border)

# 樣本邊框 - 用一個不規則形狀圈起來表示樣本
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# 計算樣本的凸包
from scipy.spatial import ConvexHull
sample_points_array = np.array(sample_points)
hull = ConvexHull(sample_points_array)
hull_points = sample_points_array[hull.vertices]

# 添加一點緩衝區
hull_path = Path(hull_points)
hull_patch = PathPatch(hull_path, facecolor='#e74c3c', alpha=0.2, edgecolor='#c0392b', linewidth=2)
ax.add_patch(hull_patch)

# 標記母體與樣本
ax.text(0.3, 0.85, '母體 (Population)', ha='center', va='center', fontsize=14, 
        bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='#2980b9'))
ax.text(0.3, 0.78, 'N = 總體數量\nμ = 母體平均數\nσ² = 母體變異數', ha='center', va='center', fontsize=12)

sample_center_x = np.mean(sample_points_array[:, 0])
sample_center_y = np.mean(sample_points_array[:, 1])
ax.text(sample_center_x, sample_center_y-0.07, '樣本 (Sample)', ha='center', va='center', fontsize=14, 
        bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='#c0392b'))
ax.text(sample_center_x, sample_center_y-0.14, 'n = 樣本數量\nx̄ = 樣本平均數\ns² = 樣本變異數', ha='center', va='center', fontsize=12)

# 抽樣與推論的箭頭 - 使用曲線箭頭
ax.annotate('抽樣 (Sampling)', 
           xy=(sample_center_x, sample_center_y), 
           xytext=(0.3, 0.55),
           fontsize=12, ha='center', va='center',
           bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='green', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                           color='green', lw=2))

ax.annotate('推論 (Inference)', 
           xy=(0.3, 0.67), 
           xytext=(sample_center_x+0.1, sample_center_y+0.02),
           fontsize=12, ha='center', va='center',
           bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='purple', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', 
                           color='purple', lw=2))

# 統計研究流程 - 右側流程圖
steps = ['研究問題定義', '資料收集', '資料分析', '統計推論']
descriptions = [
    '確定研究目標與範圍',
    '設計抽樣方式並收集數據',
    '利用統計方法處理數據',
    '基於樣本對母體做出推斷'
]
x_pos = 0.75
y_positions = np.linspace(0.8, 0.3, len(steps))

for i, (step, desc, y) in enumerate(zip(steps, descriptions, y_positions)):
    # 流程方塊
    ax.add_patch(plt.Rectangle((x_pos-0.15, y-0.05), 0.3, 0.1, 
                             facecolor=plt.cm.Blues(0.4+i*0.15), 
                             edgecolor='black', alpha=0.7))
    ax.text(x_pos, y, step, ha='center', va='center', fontsize=14, color='white')
    ax.text(x_pos+0.2, y, desc, ha='left', va='center', fontsize=12, color='black')
    
    # 流程箭頭
    if i < len(steps) - 1:
        ax.annotate('', xy=(x_pos, y_positions[i+1]+0.05), xytext=(x_pos, y-0.05), 
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))

# 標題
ax.text(0.5, 0.95, '母體與樣本關係及統計推論流程', ha='center', va='center', 
        fontsize=16, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', fc='#f8f9fa', ec='#343a40'))

# 圖例
ax.plot(0.12, 0.1, 'o', color='#3498db', markersize=5, alpha=0.4, label='母體數據點')
ax.plot(0.12, 0.05, 'o', color='#e74c3c', markersize=7, label='樣本數據點')
ax.legend(loc='lower left', fontsize=12)

# 圖例說明文字
note = ("母體：研究的完整對象集合\n"
        "樣本：從母體中抽取的子集\n"
        "抽樣：從母體選取樣本的過程\n"
        "統計推論：利用樣本特徵推估母體特徵")
ax.text(0.3, 0.1, note, fontsize=12, ha='left', va='center',
       bbox=dict(boxstyle='round,pad=0.5', fc='#f8f9fa', ec='#343a40', alpha=0.7))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

# 保存圖片
plt.savefig('parameter_statistic.png', dpi=120, bbox_inches='tight')
print(f"已生成參數與統計量關係圖：{os.path.abspath('parameter_statistic.png')}") 