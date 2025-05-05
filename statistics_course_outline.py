"""
統計學課程大綱
定義了整個課程的章節結構和內容
"""

STATISTICS_COURSE_OUTLINE = {
    "1": {
        "title": "統計學簡介與基本概念",
        "sections": [
            {"title": "統計學的定義與範疇"},
            {"title": "母體與樣本"},
            {"title": "資料類型與測量尺度"},
            {"title": "描述統計與推論統計"},
            {"title": "統計研究設計流程"},
            {"title": "資料收集方法"},
            {"title": "統計學的歷史發展與應用"}
        ]
    },
    "2": {
        "title": "資料的收集與呈現",
        "sections": [
            {"title": "抽樣方法與技巧"},
            {"title": "問卷設計原則"},
            {"title": "資料表格的建立與整理"},
            {"title": "頻率分配表"},
            {"title": "直方圖與其他圖形呈現"},
            {"title": "資料可視化技術"},
            {"title": "誤導性圖表的識別"}
        ]
    },
    "3": {
        "title": "集中趨勢與離散程度的測量",
        "sections": [
            {"title": "算術平均數"},
            {"title": "中位數與分位數"},
            {"title": "眾數"},
            {"title": "全距與四分位距"},
            {"title": "變異數與標準差"},
            {"title": "變異係數"},
            {"title": "偏態與峰度"}
        ]
    },
    "4": {
        "title": "機率論基礎",
        "sections": [
            {"title": "機率的基本概念"},
            {"title": "古典機率與相對頻率"},
            {"title": "條件機率"},
            {"title": "貝氏定理"},
            {"title": "隨機變數與機率分配"},
            {"title": "期望值與變異數"},
            {"title": "共變異數與相關係數"}
        ]
    },
    "5": {
        "title": "離散機率分配",
        "sections": [
            {"title": "伯努利試驗與二項分配"},
            {"title": "超幾何分配"},
            {"title": "泊松分配"},
            {"title": "幾何分配"},
            {"title": "負二項分配"},
            {"title": "多項分配"},
            {"title": "離散分配的應用案例"}
        ]
    },
    "6": {
        "title": "連續機率分配",
        "sections": [
            {"title": "常態分配"},
            {"title": "標準常態分配與Z轉換"},
            {"title": "指數分配"},
            {"title": "均勻分配"},
            {"title": "卡方分配"},
            {"title": "t分配"},
            {"title": "F分配"}
        ]
    },
    "7": {
        "title": "抽樣分配與中央極限定理",
        "sections": [
            {"title": "抽樣分配的概念"},
            {"title": "樣本平均數的分配"},
            {"title": "中央極限定理"},
            {"title": "樣本比例的分配"},
            {"title": "樣本變異數的分配"},
            {"title": "抽樣誤差與精確度"},
            {"title": "有限母體的抽樣校正"}
        ]
    },
    "8": {
        "title": "點估計與區間估計",
        "sections": [
            {"title": "估計量的性質"},
            {"title": "最大概似估計法"},
            {"title": "動差法"},
            {"title": "母體平均數的區間估計"},
            {"title": "母體比例的區間估計"},
            {"title": "母體變異數的區間估計"},
            {"title": "樣本大小的決定"}
        ]
    },
    "9": {
        "title": "假設檢定的基本概念",
        "sections": [
            {"title": "統計假設與檢定邏輯"},
            {"title": "第一型與第二型錯誤"},
            {"title": "顯著水準與p值"},
            {"title": "統計檢定力與樣本大小"},
            {"title": "單尾與雙尾檢定"},
            {"title": "假設檢定的步驟"},
            {"title": "假設檢定的常見誤解"}
        ]
    },
    "10": {
        "title": "單一母體的參數檢定",
        "sections": [
            {"title": "母體平均數的Z檢定"},
            {"title": "母體平均數的t檢定"},
            {"title": "母體比例的檢定"},
            {"title": "母體變異數的卡方檢定"},
            {"title": "檢定結果的詮釋"},
            {"title": "實務應用案例"},
            {"title": "使用統計軟體進行參數檢定"}
        ]
    },
    "11": {
        "title": "兩母體的參數檢定",
        "sections": [
            {"title": "獨立樣本平均數差異的檢定"},
            {"title": "配對樣本平均數差異的檢定"},
            {"title": "兩母體比例差異的檢定"},
            {"title": "兩母體變異數比的F檢定"},
            {"title": "非參數方法中的兩樣本檢定"},
            {"title": "實務應用案例"},
            {"title": "使用統計軟體進行兩樣本檢定"}
        ]
    },
    "12": {
        "title": "變異數分析",
        "sections": [
            {"title": "單因子變異數分析"},
            {"title": "多因子變異數分析"},
            {"title": "交互作用的分析"},
            {"title": "事後比較方法"},
            {"title": "變異數分析的假設檢查"},
            {"title": "實務應用案例"},
            {"title": "使用統計軟體進行變異數分析"}
        ]
    },
    "13": {
        "title": "相關與簡單線性迴歸",
        "sections": [
            {"title": "相關分析與Pearson相關係數"},
            {"title": "簡單線性迴歸模型"},
            {"title": "最小平方法"},
            {"title": "迴歸係數的檢定與區間估計"},
            {"title": "預測與信賴區間"},
            {"title": "殘差分析與模型診斷"},
            {"title": "使用統計軟體進行相關與迴歸分析"}
        ]
    },
    "14": {
        "title": "多元迴歸分析",
        "sections": [
            {"title": "多元迴歸模型的建立"},
            {"title": "多元迴歸係數的解釋"},
            {"title": "模型選擇與變數選取"},
            {"title": "多重共線性問題"},
            {"title": "類別變數與交互項"},
            {"title": "模型檢驗與診斷"},
            {"title": "使用統計軟體進行多元迴歸分析"}
        ]
    },
    "15": {
        "title": "卡方檢定與列聯表分析",
        "sections": [
            {"title": "卡方適合度檢定"},
            {"title": "獨立性檢定"},
            {"title": "同質性檢定"},
            {"title": "列聯表的風險比與勝算比"},
            {"title": "Fisher精確檢定"},
            {"title": "實務應用案例"},
            {"title": "使用統計軟體進行卡方檢定"}
        ]
    },
    "16": {
        "title": "非參數統計方法",
        "sections": [
            {"title": "非參數統計的概念與應用場景"},
            {"title": "符號檢定"},
            {"title": "Wilcoxon符號等級檢定"},
            {"title": "Mann-Whitney U檢定"},
            {"title": "Kruskal-Wallis檢定"},
            {"title": "等級相關分析"},
            {"title": "使用統計軟體進行非參數檢定"}
        ]
    }
}

# 打印每章綱要，確認結構
if __name__ == "__main__":
    for chapter_num, chapter_info in STATISTICS_COURSE_OUTLINE.items():
        print(f"第{chapter_num}章：{chapter_info['title']}")
        for i, section in enumerate(chapter_info['sections']):
            print(f"  {chapter_num}.{i+1} {section['title']}")
        print() 