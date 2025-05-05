import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import os

# Ensure directory exists
if not os.path.exists('static/images/ch10'):
    os.makedirs('static/images/ch10')

# Create t-distribution plot
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(-4, 4, 1000)
for df in [1, 5, 30]:
    ax.plot(x, stats.t.pdf(x, df), label=f'df = {df}')
ax.plot(x, stats.norm.pdf(x), 'k--', label='Normal')
ax.legend()
ax.set_title('t-分配與正態分配比較')
ax.set_xlabel('t 值')
ax.set_ylabel('機率密度')
ax.grid(True, alpha=0.3)

# Add critical regions
alpha = 0.05
df = 10
t_crit = stats.t.ppf(1-alpha/2, df)
ax.fill_between(x, 0, stats.t.pdf(x, df), where=(x >= t_crit), color='red', alpha=0.3)
ax.fill_between(x, 0, stats.t.pdf(x, df), where=(x <= -t_crit), color='red', alpha=0.3)
ax.axvline(t_crit, color='red', linestyle='--')
ax.axvline(-t_crit, color='red', linestyle='--')
ax.text(t_crit+0.1, 0.05, f't = {t_crit:.2f}', color='red')
ax.text(-t_crit-0.5, 0.05, f't = {-t_crit:.2f}', color='red')
ax.text(0, 0.01, 'Acceptance Region', ha='center')
ax.text(3, 0.05, 'Rejection Region', ha='center')
ax.text(-3, 0.05, 'Rejection Region', ha='center')

plt.tight_layout()
plt.savefig('static/images/ch10/10_2_t_test.png', dpi=150)
print('Created t-test image')

# Create a second diagram for hypothesis testing
fig, ax = plt.subplots(figsize=(10, 6))
# Draw flowchart for hypothesis testing
plt.text(0.5, 0.9, '假設檢定流程', ha='center', va='center', fontsize=18)
plt.text(0.5, 0.8, '1. 設定虛無假設(H₀)與對立假設(H₁)', ha='center', va='center')
plt.text(0.5, 0.7, '2. 選擇統計量與顯著水準(α)', ha='center', va='center')
plt.text(0.5, 0.6, '3. 收集數據與計算統計量', ha='center', va='center')
plt.text(0.5, 0.5, '4. 計算p值', ha='center', va='center')
plt.text(0.5, 0.4, '5. 比較p值與顯著水準', ha='center', va='center')
plt.text(0.5, 0.25, 'p < α ?', ha='center', va='center', fontsize=14)
plt.text(0.3, 0.15, '拒絕H₀', ha='center', va='center', fontsize=14, bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
plt.text(0.7, 0.15, '不拒絕H₀', ha='center', va='center', fontsize=14, bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))

# Draw arrows
for y1, y2 in [(0.85, 0.8), (0.75, 0.7), (0.65, 0.6), (0.55, 0.5), (0.45, 0.4), (0.35, 0.25)]:
    plt.annotate('', xy=(0.5, y2), xytext=(0.5, y1), arrowprops=dict(arrowstyle='->'))

plt.annotate('是', xy=(0.3, 0.15), xytext=(0.4, 0.25), arrowprops=dict(arrowstyle='->'))
plt.annotate('否', xy=(0.7, 0.15), xytext=(0.6, 0.25), arrowprops=dict(arrowstyle='->'))

ax.axis('off')
plt.tight_layout()
plt.savefig('static/images/ch10/10_1_hypothesis_testing.png', dpi=150)
print('Created hypothesis testing flowchart')

# Create a diagram for Type I and Type II errors
fig, ax = plt.subplots(figsize=(10, 6))
# Draw table
data = [
    ['', '虛無假設(H₀)為真', '虛無假設(H₀)為假'],
    ['不拒絕H₀', '正確決策', '第二類錯誤(β)'],
    ['拒絕H₀', '第一類錯誤(α)', '正確決策(檢定力=1-β)']
]

# Draw the table
table = ax.table(cellText=data, 
                loc='center',
                cellLoc='center',
                colWidths=[0.3, 0.35, 0.35])
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 3)

# Highlight cells
table[(1, 1)].set_facecolor('lightgreen')
table[(2, 2)].set_facecolor('lightgreen')
table[(1, 2)].set_facecolor('lightsalmon')
table[(2, 1)].set_facecolor('lightsalmon')

ax.set_title('假設檢定可能的決策結果', fontsize=16)
ax.axis('off')
plt.tight_layout()
plt.savefig('static/images/ch10/10_1_type_errors.png', dpi=150)
print('Created error types diagram') 