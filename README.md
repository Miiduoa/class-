# 統計學講義生成與網站整合系統

這個系統使用ChatGPT API生成詳細的統計學講義內容，並提供將講義整合到網站的工具。

## 系統功能

1. **講義內容生成**：使用ChatGPT生成結構化的統計學講義內容，包括主要概念、例子、記憶技巧和練習題。
2. **HTML轉換**：將生成的JSON講義文件轉換為美觀的HTML格式。
3. **本地網頁服務**：提供簡易的HTTP服務器，方便在瀏覽器中查看生成的講義。
4. **網站集成**：支持將講義內容整合到現有的學習網站中。

## 目錄結構

```
統計學/
│
├── generate_with_chatgpt.py     # ChatGPT API內容生成核心
├── statistics_course_outline.py # 課程大綱定義
├── generate_all_lectures.py     # 批量生成所有章節講義
├── json_to_html.py              # 將JSON講義轉換為HTML
├── serve_lectures.py            # 提供本地HTTP服務查看講義
├── export_to_website.py         # 將講義導出到外部網站目錄
├── integrate_to_website.py      # 通過API整合到學習網站
│
├── 講義/                        # 存放生成的JSON講義文件
│   ├── 第1章_完整.json
│   ├── 第2章_完整.json
│   └── ...
│
└── 網頁講義/                    # 存放HTML格式的講義
    ├── index.html               # 講義主頁
    ├── 第1章_完整.html
    ├── 第2章_完整.html
    └── ...
```

## 使用說明

### 1. 安裝依賴

```bash
pip install requests
```

### 2. 生成講義內容

生成所有章節的講義：

```bash
python generate_all_lectures.py --all
```

生成特定章節的講義：

```bash
python generate_all_lectures.py --chapter 1
```

合併所有章節為一個完整講義文件：

```bash
python generate_all_lectures.py --combine
```

### 3. 轉換為HTML格式

```bash
python json_to_html.py --all
```

### 4. 本地查看講義

啟動本地HTTP服務器：

```bash
python serve_lectures.py
```

然後在瀏覽器中訪問 http://localhost:8000

### 5. 整合到現有網站

#### 方法一：導出到網站目錄

```bash
python export_to_website.py --dest /path/to/your/website/statistics
```

#### 方法二：創建可部署的網站包

```bash
python integrate_to_website.py package
```

這將創建一個包含所有必要文件的ZIP包。

#### 方法三：通過API上傳到網站

```bash
python integrate_to_website.py upload --api-url https://your-website.com/api --api-key YOUR_API_KEY
```

## 問題解決

### API超時問題

如果在生成內容時遇到API超時問題，請嘗試：

1. 減少每個請求的最大令牌數（在`generate_with_chatgpt.py`中調整）
2. 增加重試次數和超時時間
3. 使用`--minimal`選項生成較短的內容

### 文件轉換問題

確保在生成JSON文件後才運行HTML轉換：

```bash
python generate_all_lectures.py --all
python json_to_html.py --all
```

## 自定義與擴展

### 修改課程大綱

編輯`statistics_course_outline.py`文件，可以調整章節和小節的結構。

### 自定義HTML樣式

編輯`json_to_html.py`中的CSS樣式，可以自定義講義的外觀。

### 添加新的整合方法

可以在`integrate_to_website.py`中添加新的整合方法，以支持不同的網站平台。

## 注意事項

- 使用前請確保有正確的ChatGPT API密鑰
- 大量生成內容可能需要較長時間，建議分批處理
- 整合到外部網站前請確保有正確的API權限 