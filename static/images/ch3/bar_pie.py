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

# 第3章 - 類別資料的圖表示例
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('類別資料的圖形呈現', fontsize=18, fontweight='bold', y=0.98)

# 設定數據
categories = ['A型', 'B型', 'O型', 'AB型']
values = [40, 26.7, 20, 13.3]
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

# ----- 左側：長條圖 -----
bars = ax1.bar(categories, values, color=colors, width=0.6, edgecolor='black', linewidth=1)
ax1.set_title('班級血型分布長條圖', fontsize=16, pad=15)
ax1.set_ylabel('百分比 (%)', fontsize=14)
ax1.set_ylim(0, 50)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 在長條上方添加數值標籤
for bar in bars:
    height = bar.get_height()
    ax1.annotate(f'{height}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3點垂直偏移
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=12, fontweight='bold')

# 添加說明文字
ax1.text(0.5, -0.15, '長條圖適合類別的大小或頻率比較', 
        ha='center', va='center', transform=ax1.transAxes, 
        fontsize=12, style='italic',
        bbox=dict(boxstyle='round,pad=0.5', fc='#f8f9fa', ec='#343a40', alpha=0.7))

# ----- 右側：圓餅圖 -----
# 用於標示顯眼的圓餅圖文字
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return f'{pct:.1f}%\n({val}人)'
    return my_format

# 突出A型（假設它是我們要強調的部分）
explode = (0.1, 0, 0, 0)

# 繪製圓餅圖
wedges, texts, autotexts = ax2.pie(values, 
                                  labels=categories, 
                                  autopct=autopct_format(values),
                                  explode=explode,
                                  colors=colors,
                                  shadow=True, 
                                  startangle=90,
                                  textprops={'fontsize': 12})

# 設置自動文字標籤的樣式
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')

ax2.set_title('班級血型分布圓餅圖', fontsize=16, pad=15)
ax2.axis('equal')  # 確保圓餅是圓形

# 添加說明文字
ax2.text(0.5, -0.15, '圓餅圖適合顯示各部分佔整體的比例', 
        ha='center', va='center', transform=ax2.transAxes, 
        fontsize=12, style='italic',
        bbox=dict(boxstyle='round,pad=0.5', fc='#f8f9fa', ec='#343a40', alpha=0.7))

# 添加數據來源說明
plt.figtext(0.5, 0.01, '資料來源：某班30位學生血型調查 (A:12人, B:8人, O:6人, AB:4人)', 
           ha='center', fontsize=10, style='italic')

# 調整子圖間距
plt.tight_layout(rect=[0, 0.05, 1, 0.95])

# 保存圖片
plt.savefig('bar_pie.png', dpi=120, bbox_inches='tight')
print(f"已生成長條圖與圓餅圖：{os.path.abspath('bar_pie.png')}") 