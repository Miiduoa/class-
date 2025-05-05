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

# 第1章 - 統計學流程示意圖
fig, ax = plt.subplots(figsize=(10, 5))
steps = ['資料收集', '資料整理', '資料分析', '統計推論']
x = np.arange(len(steps))
ax.plot(x, [1, 1, 1, 1], 'bo-', linewidth=2, markersize=12)

# 繪製步驟說明框
for i, (step, xi) in enumerate(zip(steps, x)):
    ax.text(xi, 1.2, step, ha='center', va='center', fontsize=14,
           bbox=dict(boxstyle='round,pad=0.5', fc='skyblue', ec='blue', alpha=0.7))
    
    # 為每個步驟添加簡短說明
    descriptions = [
        '透過抽樣、實驗\n或既有資料庫\n取得數據',
        '對原始數據進行\n分類、編碼和\n清理',
        '應用統計方法\n計算、檢定\n與圖表呈現',
        '根據樣本數據\n對母體推論\n做出決策'
    ]
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
ax.set_title('統計學四大流程示意圖', fontsize=16)

# 調整圖的範圍以適應所有元素
ax.set_xlim(-0.5, len(steps)-0.5)
ax.set_ylim(0.5, 1.5)

# 保存圖片
plt.savefig('process_flow.png', dpi=120, bbox_inches='tight')
print(f"已生成流程圖：{os.path.abspath('process_flow.png')}") 