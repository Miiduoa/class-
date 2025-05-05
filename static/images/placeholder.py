#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os

# 創建一個預設的佔位圖片
fig, ax = plt.subplots(figsize=(8, 6))

# 設置背景顏色
ax.set_facecolor('#f8f9fa')
plt.gcf().patch.set_facecolor('#f8f9fa')

# 繪製一個圖片圖標
# 繪製圖片框架
rect = plt.Rectangle((0.25, 0.25), 0.5, 0.5, fill=False, 
                    edgecolor='#6c757d', linewidth=4, linestyle='-')
ax.add_patch(rect)

# 繪製山和太陽
triangle = plt.Polygon([[0.35, 0.45], [0.5, 0.65], [0.65, 0.45]], 
                      closed=True, fill=True, color='#6c757d', alpha=0.7)
ax.add_patch(triangle)
circle = plt.Circle((0.7, 0.65), 0.08, color='#6c757d', alpha=0.7)
ax.add_patch(circle)

# 添加文字
ax.text(0.5, 0.2, '圖片載入中...', ha='center', va='center', 
       fontsize=16, color='#343a40')
ax.text(0.5, 0.15, '請檢查圖片路徑是否正確', ha='center', va='center', 
       fontsize=12, color='#6c757d')

# 移除座標軸
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# 設置圖形範圍
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# 保存圖片
plt.savefig('placeholder.png', dpi=100, bbox_inches='tight')
print(f"已生成佔位圖：{os.path.abspath('placeholder.png')}") 