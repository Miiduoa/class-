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

# 創建一個專業的示範誤導性圖表的視覺化
fig = plt.figure(figsize=(15, 10))
fig.suptitle('統計圖表的優質性與扭曲性', fontsize=20, fontweight='bold')

# 添加一些說明文字
plt.figtext(0.5, 0.94, '以下展示常見的圖表設計陷阱以及如何識別它們', 
           ha='center', fontsize=14, style='italic')

# 創建2x2的子圖布局
axes = fig.subplots(2, 2)

# ----- 圖1：Y軸截斷 -----
# 例子：公司收入成長
years = np.array([2018, 2019, 2020, 2021, 2022])
revenue = np.array([100, 105, 107, 109, 110])  # 只有微小的增長

# 正確的圖表
ax1 = axes[0, 0]
ax1.plot(years, revenue, 'o-', linewidth=2, markersize=8, color='#3498db')
ax1.set_title('正確表示：完整Y軸比例尺', fontsize=14)
ax1.set_xlabel('年份', fontsize=12)
ax1.set_ylabel('收入 (百萬元)', fontsize=12)
ax1.set_ylim(0, max(revenue) * 1.1)  # 從0開始
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_xticks(years)
for i, v in enumerate(revenue):
    ax1.annotate(str(v), (years[i], v), 
                xytext=(0, 5), textcoords='offset points',
                ha='center', fontweight='bold')

# 誤導性的圖表：截斷Y軸
ax2 = axes[0, 1]
ax2.plot(years, revenue, 'o-', linewidth=2, markersize=8, color='#e74c3c')
ax2.set_title('誤導性表示：截斷的Y軸', fontsize=14)
ax2.set_xlabel('年份', fontsize=12)
ax2.set_ylabel('收入 (百萬元)', fontsize=12)
ax2.set_ylim(95, max(revenue) * 1.05)  # 從95開始
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.set_xticks(years)
for i, v in enumerate(revenue):
    ax2.annotate(str(v), (years[i], v), 
                xytext=(0, 5), textcoords='offset points',
                ha='center', fontweight='bold')

# 添加截斷標記和警告說明
ax2.axhline(y=ax2.get_ylim()[0], color='#e74c3c', linestyle='-', linewidth=2)
ax2.text(years[0]-0.5, ax2.get_ylim()[0]+1, '截斷！', 
         color='#e74c3c', fontweight='bold', fontsize=12)
ax2.text((years[0]+years[-1])/2, ax2.get_ylim()[0]+2, 
         '此處Y軸從95開始，誇大了變化幅度',
         ha='center', color='#e74c3c', fontsize=10, style='italic',
         bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#e74c3c', alpha=0.7))

# ----- 圖2：不恰當的圖表類型 -----
# 時間序列數據的呈現方式 - 使用同樣的數據
ax3 = axes[1, 0]
ax3.plot(years, revenue, 'o-', linewidth=2, markersize=8, color='#3498db')
ax3.set_title('合適的圖表：折線圖展示趨勢', fontsize=14)
ax3.set_xlabel('年份', fontsize=12)
ax3.set_ylabel('收入 (百萬元)', fontsize=12)
ax3.grid(True, linestyle='--', alpha=0.7)
ax3.set_xticks(years)

# 誤導性：使用不恰當的圖表類型
ax4 = axes[1, 1]
ax4.pie(revenue, labels=[f'{y}年' for y in years], 
       autopct='%1.1f%%', startangle=90,
       colors=plt.cm.Paired(np.linspace(0,1,len(revenue))))
ax4.set_title('誤導性表示：圓餅圖不適合時間趨勢', fontsize=14)
ax4.text(0, -1.3, '圓餅圖應用於展示部分與整體關係，不適合時間趨勢！',
        ha='center', color='#e74c3c', fontsize=12, style='italic',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#e74c3c', alpha=0.7))

# 添加解釋文本框
explanation = """
常見的圖表扭曲技巧：
1. Y軸截斷：從非零值開始Y軸使差異看起來更顯著
2. 不恰當的圖表類型：選用不適合數據類型的圖表形式
3. 缺乏標籤或比例尺：隱藏關鍵信息使比較困難
4. 誤導性的顏色或視覺效果：使用3D或陰影突出某些數據
5. 選擇性呈現：僅展示有利的數據點或時間區間

如何識別：檢查Y軸起點、比較比例尺、理解數據類型並選擇合適圖表
"""

# 在圖表下方添加說明文字框
plt.figtext(0.5, 0, explanation, 
           ha='center', va='bottom', fontsize=12, 
           bbox=dict(boxstyle='round,pad=1', fc='#f8f9fa', ec='#343a40', alpha=0.8))

# 調整布局
plt.tight_layout(rect=[0, 0.07, 1, 0.93])
plt.subplots_adjust(bottom=0.25)  # 為底部文字框留出空間

# 保存圖片
plt.savefig('misleading_graph.png', dpi=120, bbox_inches='tight')
print(f"已生成誤導性圖表示例：{os.path.abspath('misleading_graph.png')}") 