import os
import openai
from flask import current_app as app
import datetime
import json

# OpenAI API設置
OPENAI_API_KEY = "sk-uYf5DnpjM2xaHE1p261310C081E94d5a8aF0D61cE3F6Bf68"  # 用戶提供的API密鑰
OPENAI_API_BASE = "https://free.v36.cm/v1"  # 確保添加v1路徑

# API狀態變量
API_STATUS = {
    "connected": False,
    "message": "尚未連接到API",
    "last_test_time": None
}

# 測試模式設置
TEST_MODE = False  # 嘗試使用API，只有在連接失敗時才使用測試模式

# 系統初始化訊息
print("統計學助手初始化中... 正在嘗試連接API服務")

# 初始化OpenAI客戶端
client = None

def test_api_connection(api_key=None, api_base=None):
    """測試API連接並更新連接狀態"""
    global client, TEST_MODE, API_STATUS
    
    # 如果提供了新的API密鑰和基礎URL，則更新全局變量
    if api_key:
        global OPENAI_API_KEY
        OPENAI_API_KEY = api_key
    
    if api_base:
        global OPENAI_API_BASE
        # 確保API基礎URL以/v1結尾
        if not api_base.endswith('/v1'):
            api_base = api_base + '/v1' if not api_base.endswith('/') else api_base + 'v1'
        OPENAI_API_BASE = api_base
    
    print(f"嘗試連接API，使用URL: {OPENAI_API_BASE} 和 API密鑰: {OPENAI_API_KEY[:5]}...")
    
    try:
        from openai import OpenAI
        # 創建新的客戶端實例
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
        
        # 測試連接
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "測試"}],
                max_tokens=5
            )
            
            # 更新API狀態
            API_STATUS = {
                "connected": True,
                "message": f"API連接成功! 響應: {response}",
                "last_test_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"API連接成功! 響應: {response}")
            TEST_MODE = False  # 確認連接成功，使用API模式
            return True, f"API連接成功! 可以正常使用聊天功能。"
        except Exception as api_call_e:
            error_msg = f"API客戶端已初始化，但API調用失敗: {str(api_call_e)}"
            print(error_msg)
            
            # 更新API狀態
            API_STATUS = {
                "connected": False,
                "message": error_msg,
                "last_test_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            TEST_MODE = True  # API調用失敗，切換到測試模式
            return False, error_msg
    
    except Exception as init_e:
        # 更新API狀態
        error_msg = f"API客戶端初始化失敗: {str(init_e)}"
        API_STATUS = {
            "connected": False,
            "message": error_msg,
            "last_test_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(error_msg)
        TEST_MODE = True  # 初始化失敗，切換到測試模式
        print("切換至測試模式 - 使用本地模擬回答")
        return False, error_msg

# 嘗試初始連接
test_api_connection()

def generate_explanation(topic, difficulty="intermediate"):
    """
    為指定的統計學主題生成解釋
    
    參數:
        topic (str): 要解釋的統計學主題或概念
        difficulty (str): 難度級別 (beginner, intermediate, advanced)
    
    返回:
        str: 生成的解釋文本
    """
    if TEST_MODE or client is None:
        # 測試模式或客戶端初始化失敗：提供模擬數據而不調用API
        return get_mock_explanation(topic, difficulty)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": f"你是一位專業的統計學教師，專長於用清晰易懂的方式解釋複雜概念。請以{difficulty}難度解釋以下統計學概念。"},
                {"role": "user", "content": f'請解釋統計學中的"{topic}"概念。提供易於理解的定義、實際應用範例，以及這個概念的重要性。'}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # 驗證響應結構
        if hasattr(response, 'choices') and len(response.choices) > 0 and hasattr(response.choices[0], 'message'):
            return response.choices[0].message.content
        else:
            app.logger.error(f"API返回無效響應結構: {response}")
            return get_mock_explanation(topic, difficulty)
            
    except Exception as e:
        app.logger.error(f"ChatGPT API調用失敗: {str(e)}")
        # 出現錯誤時返回模擬數據，而不是錯誤信息
        return get_mock_explanation(topic, difficulty)

def generate_practice_questions(topic, number=3, difficulty="intermediate"):
    """
    為指定的統計學主題生成練習題
    
    參數:
        topic (str): 統計學主題
        number (int): 要生成的題目數量
        difficulty (str): 難度級別 (beginner, intermediate, advanced)
    
    返回:
        str: 包含問題和答案的文本
    """
    print(f"[generate_practice_questions] 開始生成練習題： 主題={topic}, 數量={number}, 難度={difficulty}")
    
    if TEST_MODE or client is None:
        # 測試模式或客戶端初始化失敗：提供模擬數據而不調用API
        print(f"[generate_practice_questions] 在測試模式下生成練習題")
        return get_mock_practice_questions(topic, number, difficulty)
    
    try:
        print(f"[generate_practice_questions] 嘗試通過API生成練習題")
        
        # 確保參數類型正確
        try:
            number = int(number)
        except (ValueError, TypeError):
            print(f"[generate_practice_questions] 數量參數無效，使用默認值: 3")
            number = 3
            
        # 驗證難度級別
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        if difficulty not in valid_difficulties:
            print(f"[generate_practice_questions] 難度參數無效: {difficulty}，使用默認值: intermediate")
            difficulty = "intermediate"
        
        # 根據難度級別調整提示詞
        difficulty_prompt = {
            "beginner": "基礎難度，適合初學者，使用簡單計算和基本概念",
            "intermediate": "中等難度，需要綜合應用多個概念，適合具有一定基礎的學習者",
            "advanced": "高級難度，需要深入理解和複雜計算，適合進階學習者"
        }.get(difficulty, "中等難度，需要綜合應用多個概念")
        
        system_prompt = f"""你是一位專業的統計學教師，專長於創建教育性的練習題。
請創建{number}道關於"{topic}"的{difficulty_prompt}的練習題。

每道題目必須包含：
1. 清晰的問題描述
2. 詳細的解答過程
3. 如果適用，包含必要的公式和計算步驟

請確保答案詳盡且教育性強，幫助學生真正理解概念。使用繁體中文回答。"""
        
        print(f"[generate_practice_questions] 發送API請求 - 系統提示: {system_prompt[:100]}...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'請為"{topic}"這個統計學主題創建{number}道練習題，每道題都應包含問題和詳細解答。提供具有教育價值的題目，展示這個概念的實際應用。'}
                ],
                temperature=0.7,
                max_tokens=2500  # 增加token上限以獲得更詳細的回答
            )
            
            # 打印API響應詳情 (注意不要打印敏感信息)
            response_details = f"模型: {response.model}, 選項數: {len(response.choices)}"
            print(f"[generate_practice_questions] API響應詳情: {response_details}")
            
            # 檢查響應結構
            if not hasattr(response, 'choices') or len(response.choices) == 0:
                print(f"[generate_practice_questions] API返回的響應缺少選項")
                return get_mock_practice_questions(topic, number, difficulty)
                
            if not hasattr(response.choices[0], 'message'):
                print(f"[generate_practice_questions] API返回的選項缺少消息內容")
                return get_mock_practice_questions(topic, number, difficulty)
                
            result = response.choices[0].message.content
            if not result or len(result.strip()) == 0:
                print(f"[generate_practice_questions] API返回的消息內容為空")
                return get_mock_practice_questions(topic, number, difficulty)
                
            print(f"[generate_practice_questions] 成功獲取API響應，內容長度: {len(result)}")
            print(f"[generate_practice_questions] 內容預覽: {result[:100]}...")
            return result
            
        except Exception as api_e:
            error_msg = f"[generate_practice_questions] API調用出錯: {str(api_e)}"
            app.logger.error(error_msg)
            print(error_msg)
            return get_mock_practice_questions(topic, number, difficulty)
            
    except Exception as e:
        error_msg = f"[generate_practice_questions] 生成練習題過程中出錯: {str(e)}"
        app.logger.error(error_msg)
        print(error_msg)
        # 確保在出錯時總是返回有用的內容，而不是拋出異常
        return get_mock_practice_questions(topic, number, difficulty)

def generate_study_plan(topics, duration_weeks=4, goal=None, current_level=None, weekly_hours=None, include_resources=True):
    """
    生成統計學學習計劃
    
    參數:
        topics (list): 要學習的主題列表
        duration_weeks (int): 學習計劃的持續時間（以週為單位）
        goal (str): 學習目標
        current_level (str): 目前知識水平
        weekly_hours (int): 每週可投入學習時間
        include_resources (bool): 是否包含推薦資源
    
    返回:
        dict: 生成的學習計劃，結構化JSON格式
    """
    print(f"開始生成學習計劃: 主題={topics}, 週數={duration_weeks}, 目標={goal}, 級別={current_level}, 每週時間={weekly_hours}")
    
    if TEST_MODE or client is None:
        # 測試模式或客戶端初始化失敗：提供模擬數據而不調用API
        print("在測試模式下生成學習計劃")
        return get_mock_study_plan(topics, duration_weeks)
    
    # 轉換主題列表為字符串，如果是列表的話
    if isinstance(topics, list):
        topics_str = ", ".join(topics)
    else:
        topics_str = topics

    # 確保duration_weeks是整數
    try:
        duration_weeks = int(duration_weeks)
    except (ValueError, TypeError):
        duration_weeks = 4
        print(f"持續時間轉換為整數失敗，使用默認值: {duration_weeks}")
        
    # 構建用戶提示
    user_prompt = f'請為以下統計學主題設計一個{duration_weeks}週的學習計劃：{topics_str}。'
    
    # 添加附加信息
    if goal:
        user_prompt += f' 學習目標是：{goal}。'
    
    if current_level:
        level_descriptions = {
            'beginner': '初學者，無統計基礎',
            'intermediate': '中級，已了解基本概念',
            'advanced': '進階，已掌握多數統計方法'
        }
        level_desc = level_descriptions.get(current_level, current_level)
        user_prompt += f' 學習者目前的知識水平是：{level_desc}。'
    
    if weekly_hours:
        user_prompt += f' 每週可投入約{weekly_hours}小時學習。'
    
    if include_resources:
        user_prompt += ' 請包含推薦的學習資源和參考資料。'
    
    user_prompt += ' 計劃應包含每週的學習目標、具體學習內容和自我評估方法。'
    
    # 系統提示，要求輸出JSON格式
    system_prompt = """你是一位專業的統計學教育顧問，專長於設計個性化學習計劃。

請根據用戶提供的信息，設計結構化、實用的統計學學習計劃，並以JSON格式返回。格式如下：

{
  "overview": "學習計劃概述...",
  "weeks": [
    {
      "title": "第1週：基礎概念",
      "focus": "主要重點",
      "description": "本週描述...",
      "topics": ["主題1", "主題2", "主題3"],
      "activities": ["活動1", "活動2", "活動3"]
    }
  ],
  "resources": [
    {
      "title": "資源名稱",
      "description": "資源描述..."
    }
  ]
}

確保計劃的進度合理，難度逐步提升，概念互相連貫。使用清晰的繁體中文回答。"""
    
    print(f"發送到API的學習計劃提示: {user_prompt[:100]}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}  # 要求JSON格式回應
        )
        
        # 驗證響應結構
        if hasattr(response, 'choices') and len(response.choices) > 0 and hasattr(response.choices[0], 'message'):
            result = response.choices[0].message.content
            print(f"成功生成學習計劃，內容長度: {len(result)}")
            
            # 嘗試將結果解析為JSON
            try:
                # 檢查是否包含```json 等標記，如果有就提取實際JSON內容
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                    print(f"提取標記內的JSON：{result[:50]}...")
                
                # 清理可能存在的特殊格式標記
                result = result.replace("```", "").strip()
                
                # 解析JSON
                plan_data = json.loads(result)
                print(f"成功解析JSON數據，包含鍵: {', '.join(plan_data.keys())}")
                return plan_data
            except json.JSONDecodeError as e:
                print(f"API回傳的內容無法被解析為JSON: {e}")
                print(f"問題內容: {result[:200]}")
                # 返回文本內容作為overview
                return {
                    "overview": "學習計劃生成時出現格式問題，但我們仍然整理了以下內容：",
                    "weeks": [{"title": f"第1-{duration_weeks}週", "description": result, "topics": [topics_str]}],
                    "resources": []
                }
        else:
            app.logger.error(f"API返回無效響應結構: {response}")
            print(f"API返回無效響應結構，使用模擬數據")
            return get_mock_study_plan(topics, duration_weeks)
            
    except Exception as e:
        error_msg = f"生成學習計劃時發生錯誤: {str(e)}"
        app.logger.error(error_msg)
        print(error_msg)
        # 出現錯誤時返回模擬數據，而不是錯誤信息
        return get_mock_study_plan(topics, duration_weeks)

def generate_chat_response(message, history=None):
    """
    生成對話回覆
    
    參數:
        message (str): 用戶輸入的訊息
        history (list): 對話歷史記錄，格式為[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    
    返回:
        str: 生成的回覆
    """
    try:
        # 首先檢查是否在測試模式或者API不可用
        if TEST_MODE or client is None:
            print(f"使用模擬回答系統處理問題: {message}")
            return get_smart_mock_response(message)
        
        # 以下是正常的API調用流程，當TEST_MODE為False時執行
        print(f"正在通過OpenAI API處理問題: {message}")
        
        # 構建訊息列表
        system_message = """你是一位專業的統計學教授，名為「統計學助手」。擁有豐富的統計學知識和教學經驗。
            
專長領域包括：
1. 描述統計與推論統計
2. 機率分配理論
3. 假設檢定
4. 迴歸分析
5. 變異數分析
6. 非參數統計方法

回答特點：
- 提供深入而清晰的統計學概念解釋
- 使用恰當的實例和比喻來說明複雜概念
- 對於公式和理論，會提供直觀解釋並解釋其應用場景
- 對統計誤解進行糾正，避免常見的統計謬誤
- 區分不同統計學流派的觀點（如頻率學派與貝葉斯學派）
- 根據學生的問題難度調整回答深度

當遇到不確定的問題時，不要猜測答案，而是坦誠表明限制並提供學習建議。專業、友善、耐心，並樂於解答任何統計學相關問題。

請以專業、簡潔但內容豐富的方式回答。對複雜問題提供分步驟的清晰解釋。優先以繁體中文回答。"""
        
        messages = [{"role": "system", "content": system_message}]
        
        # 添加對話歷史
        if history and isinstance(history, list):
            messages.extend(history[-10:])  # 限制歷史記錄長度，只使用最近的10條消息
        
        # 添加當前用戶訊息
        messages.append({"role": "user", "content": message})
        
        # 詳細日誌
        print(f"發送至OpenAI API的消息: {messages}")
        
        # 嘗試API調用
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 驗證響應結構
        if hasattr(response, 'choices') and len(response.choices) > 0 and hasattr(response.choices[0], 'message'):
            print("成功從OpenAI API獲取回應")
            return response.choices[0].message.content
        else:
            app.logger.error(f"API返回無效響應結構: {response}")
            print(f"API返回了無效的響應結構: {response}")
            # 返回模擬數據作為備用
            return get_smart_mock_response(message)
            
    except Exception as e:
        app.logger.error(f"ChatGPT API調用失敗: {str(e)}")
        print(f"與OpenAI API通信時發生錯誤: {str(e)}")
        # 出現錯誤時返回模擬數據
        return get_smart_mock_response(message)

# 測試模式的模擬數據函數
def get_mock_explanation(topic, difficulty):
    """提供模擬的概念解釋，根據難度提供不同深度的內容"""
    difficulty_level = {"beginner": "基礎", "intermediate": "中級", "advanced": "高級"}
    level = difficulty_level.get(difficulty, "中級")
    
    if topic == "標準差":
        if difficulty == "beginner":
            return f"""【{level}難度】標準差解釋

**標準差是什麼？**

標準差是一個數字，告訴我們一組數據的分散程度。簡單來說，它告訴我們數據點平均離開平均值有多遠。

**直觀理解**：
想像一下，你測量了班上10位同學的身高：
- 如果所有人身高都差不多（比如都在170-172公分之間），標準差就會很小
- 如果身高差異很大（有的150公分，有的195公分），標準差就會很大

**日常生活例子**：
1. **氣溫波動**：某地夏季氣溫標準差小，表示溫度很穩定；冬季標準差大，表示溫度變化大。
2. **生產質量**：工廠生產的零件尺寸標準差小，表示產品一致性好。
3. **考試成績**：班級考試分數標準差小，表示大家程度差不多；標準差大，表示學生程度差異大。

**為什麼標準差重要？**
- 幫助我們了解數據的穩定性和可靠性
- 讓我們知道平均值是否能代表整體情況
- 用來比較不同組數據的分散程度

標準差是統計學中最基本也最實用的工具之一，即使不懂複雜數學，理解它的概念也能幫助我們做出更好的決策。
"""
        elif difficulty == "intermediate":
            return f"""【{level}難度】標準差解釋

標準差是統計學中常用的離散程度衡量指標，用於量化數據分佈的離散或變異程度。

**定義**：
標準差是方差的平方根，計算方法如下：
- 樣本標準差 s = √[Σ(xi - x̄)²/(n-1)]
- 母體標準差 σ = √[Σ(xi - μ)²/N]

其中：
- xi 是個別觀測值
- x̄ 是樣本平均數
- μ 是母體平均數
- n 是樣本數量
- N 是母體數量

**實際應用**：
1. **金融風險評估**：投資組合風險管理中，標準差常被用來衡量投資回報的波動性。
2. **品質控制**：製造業中用於監控產品尺寸的一致性。
3. **氣象預測**：評估溫度、降雨量等天氣數據的變異性。
4. **醫學研究**：分析實驗結果或檢測值的穩定性。

**常態分佈中的標準差**：
在常態分佈中，大約68%的數據落在平均數±1個標準差範圍內，95%落在±2個標準差範圍內，99.7%落在±3個標準差範圍內。這被稱為68-95-99.7規則或三西格瑪法則。

**重要性**：
標準差具有以下特點使其成為統計學的核心概念：
1. 與原始數據單位一致，易於解釋
2. 能有效識別離群值和異常情況
3. 為其他統計分析（如假設檢定、區間估計）提供基礎
4. 用於評估測量的精確度和準確度

標準差是數據分析中不可或缺的工具，能幫助我們更科學地評估數據的變異性和不確定性。
"""
        else:  # advanced
            return f"""【{level}難度】標準差解釋

標準差是衡量統計分佈離散程度的重要參數，從概率論和統計推斷的角度，它具有深厚的理論基礎和廣泛的應用。

**數學定義與推導**：
給定隨機變量X的分佈，其方差定義為：
σ² = E[(X - μ)²] = ∫(x - μ)²f(x)dx

對於離散數據集{{x₁, x₂, ..., xₙ}}，母體標準差σ和樣本標準差s分別為：
- 母體標準差：σ = √[Σ(xᵢ - μ)²/N]
- 樣本標準差：s = √[Σ(xᵢ - x̄)²/(n-1)]

樣本標準差使用n-1作為分母（貝塞爾校正），原因是：
- 使估計量無偏，E(s²) = σ²
- 修正因使用樣本均值x̄估計未知母體均值μ而引入的自由度損失

**高級統計推斷中的應用**：
1. **標準誤差與置信區間**：
   - 樣本均值的標準誤 SE(x̄) = s/√n
   - 95%置信區間：x̄ ± t₍ₙ₋₁,₀.₀₂₅₎×SE(x̄)
   
2. **假設檢定中的應用**：
   - t統計量：t = (x̄ - μ₀)/(s/√n)，服從自由度為n-1的t分佈
   - 功效分析：β = Φ(zₐ - μ₁/σ√n) - Φ(-zₐ - μ₁/σ√n)

3. **多變量分析中的擴展**：
   - 樣本協方差矩陣S作為標準差在多維空間的推廣
   - 馬氏距離(x-μ)'Σ⁻¹(x-μ)作為標準化距離的多維類比

**理論上的特性與限制**：
1. **穩健性問題**：標準差對離群值高度敏感，在重尾分佈中可能不是最佳離散度量
2. **替代量與改進**：
   - 平均絕對偏差(MAD)：對離群值較不敏感
   - 四分位距(IQR)：完全基於順序統計量
   - 修剪標準差：排除極端值後計算

3. **統計效率**：在常態分佈假設下，樣本標準差是母體標準差的最大似然估計量，且漸近有效

4. **不確定性量化**：標準差的標準誤 SE(s) = σ/√(2(n-1))，可用於構建關於σ的置信區間

在高級數據分析中，理解標準差的理論基礎、假設條件和統計特性至關重要，特別是在處理非常態數據、小樣本或進行精細推斷時。
"""
    elif topic == "假設檢定":
        if difficulty == "beginner":
            return f"""【{level}難度】假設檢定解釋

**假設檢定是什麼？**

假設檢定是一種判斷方法，用來確定我們的猜想（假設）是否可能是真的。它就像科學實驗一樣，通過數據來驗證我們的想法。

**簡單例子**：
想像你認為一枚硬幣是公平的（一半機會正面，一半機會反面）。你可以拋這枚硬幣100次來檢驗這個想法：
- 如果正面出現了大約50次，說明硬幣可能是公平的
- 如果正面出現了80次，說明硬幣可能不公平

**假設檢定的基本步驟**：
1. 提出兩個對立的猜想：
   - 虛無假設（默認想法）：例如"硬幣是公平的"
   - 對立假設（我們想證明的）：例如"硬幣不公平"
2. 收集數據
3. 看數據是否支持我們的猜想
4. 做出結論

**生活中的例子**：
1. **藥物測試**：新藥是否比安慰劑更有效？
2. **民意調查**：兩位候選人的支持率是否真的有差異？
3. **產品改進**：新包裝是否真的讓銷售增加了？

**基本概念**：
- **p值**：數據支持虛無假設的可能性有多大，越小越不支持
- **顯著性水平**：通常設為0.05，如果p值小於它，我們拒絕虛無假設

假設檢定幫助我們避免主觀判斷，使用數據科學地做決策，是現代研究和商業分析的基礎工具。
"""
        elif difficulty == "intermediate":
            return f"""【{level}難度】假設檢定解釋

假設檢定是統計學中用於判斷樣本數據是否足以支持某個關於母體的假設的系統方法。

**基本概念**：
假設檢定是一個統計決策過程，通過對立兩個假設進行評估：
1. **虛無假設 (H₀)**：代表"沒有效應"或"沒有差異"的陳述。
2. **對立假設 (H₁或Ha)**：代表研究者試圖證明的陳述。

**檢定統計量與抽樣分佈**：
檢定統計量是根據樣本數據計算的值，用於評估虛無假設。常見的檢定統計量包括：
- Z統計量：當母體標準差已知且樣本量大時使用
- t統計量：當母體標準差未知且假設母體近似常態分佈時使用
- F統計量：用於比較兩個或多個總體的方差
- χ²統計量：用於類別數據的分析

**基本步驟**：
1. 提出虛無假設和對立假設
2. 選擇顯著水準(α)，通常為0.05或0.01
3. 收集數據並計算檢定統計量
4. 計算p值或確定臨界區域
5. 做出統計決策並解釋結果

**p值與統計顯著性**：
p值是在虛無假設為真的條件下，觀察到的檢定統計量或更極端值出現的概率。如果p值小於顯著水準α，則拒絕虛無假設。

**常見檢定類型**：
1. **單樣本檢定**：比較樣本與已知或假設的母體參數
2. **獨立樣本檢定**：比較兩個獨立樣本的參數
3. **配對樣本檢定**：比較相同樣本在不同條件下的參數
4. **卡方檢定**：分析類別變數之間的關聯

**實際應用**：
1. **醫學研究**：評估新藥是否比安慰劑更有效。
2. **市場調查**：確定消費者是否偏好某個新產品。
3. **品質控制**：判斷生產流程變更是否改善了產品質量。
4. **社會科學**：檢驗不同人口群體間是否存在顯著差異。

**第一類和第二類錯誤**：
- 第一類錯誤(α)：錯誤地拒絕真的虛無假設（虛假陽性）
- 第二類錯誤(β)：錯誤地接受假的虛無假設（虛假陰性）
- 檢定的功效 = 1-β：正確拒絕假的虛無假設的概率

理解假設檢定讓我們能夠基於數據而非直覺做出決策，是現代統計推斷的核心工具。
"""
        else:  # advanced
            return f"""【{level}難度】假設檢定解釋

假設檢定是統計推斷的核心方法論，源自Neyman-Pearson假設檢定框架，它提供了一套嚴謹的程序來評估關於母體參數的統計假設。

**理論基礎與推導**：

假設檢定建立在抽樣分佈理論之上。給定隨機變量X服從分佈f(x;θ)，我們對參數θ進行推斷：
- 虛無假設 H₀: θ ∈ Θ₀
- 對立假設 H₁: θ ∈ Θ₁

檢定過程涉及構造檢定統計量T(X)和拒絕域R，使得：
- 當T(X) ∈ R時，拒絕H₀
- 當T(X) ∉ R時，不拒絕H₀

**最優檢定理論**：

Neyman-Pearson引理指出，當簡單假設H₀: θ = θ₀對比H₁: θ = θ₁時，最優檢定基於似然比：
L(X) = f(X;θ₁)/f(X;θ₀)

拒絕域為{{X: L(X) > k}}，其中k是使得P₀(L(X) > k) = α的常數。

對於複合假設，常使用廣義似然比檢定(GLRT)：
λ(X) = sup{{L(θ;X): θ ∈ Θ₀}} / sup{{L(θ;X): θ ∈ Θ}}

**漸近理論**：

在大樣本條件下，-2log(λ)漸近服從自由度為dim(Θ)-dim(Θ₀)的卡方分佈，這構成了許多參數檢定的基礎。

**多重檢定問題**：

當同時進行多個假設檢定時，第一類錯誤率會累積增大，需要控制族錯誤率(FWER)或錯誤發現率(FDR)：
- Bonferroni校正：α* = α/m
- Benjamini-Hochberg程序：控制FDR在預設水平q
- Holm's逐步程序：提供比Bonferroni更強的FWER控制

**貝氏視角的假設檢定**：

貝葉斯因子(BF)提供了替代頻率學派p值的方法：
BF₁₀ = P(data|H₁)/P(data|H₀)

BF₁₀ > 1表示數據支持H₁，BF₁₀ < 1表示數據支持H₀，解釋不依賴樣本量和停止規則。

**檢定力分析與樣本量設計**：

檢定力1-β是正確拒絕假的H₀的概率，受多因素影響：
- 效應大小d（標準化的參數差異）
- 顯著性水平α
- 樣本量n
- 檢定類型（單尾vs雙尾）

所需樣本量可通過以下關係估計：
n ≈ (z₁₋ₐ + z₁₋ᵦ)²/(d²)

**非參數假設檢定進展**：

傳統參數檢定往往依賴分佈假設，非參數方法提供更靈活的選擇：
- 重抽樣方法（Bootstrap、置換檢定）
- 秩檢定（Wilcoxon、Mann-Whitney U等）
- 分位數回歸檢定

**檢定的統計哲學爭議**：

顯著性假設檢定(NHST)面臨的批評：
- 二元決策（顯著vs非顯著）忽略實際意義
- p-hacking和出版偏倚
- 混淆統計顯著性與實際重要性

替代方法包括：
- 效應大小報告和置信區間
- 貝氏方法
- 模型選擇準則（AIC、BIC等）

理解假設檢定的深層理論基礎和局限性，有助於在複雜研究中正確應用統計推斷方法，避免常見陷阱和誤解。
"""
    else:
        # 為其他主題提供三種不同難度的模板
        if difficulty == "beginner":
            return f"""【{level}難度】{topic}解釋

**{topic}是什麼？**

{topic}是統計學中的一個重要概念，它幫助我們理解和分析數據。用簡單的話來說，{topic}讓我們能夠從數字中得出有意義的結論。

**日常生活中的例子**：
1. **購物決策**：比較不同商店的價格，找出最划算的選擇
2. **天氣預報**：根據過去的天氣數據來預測未來的天氣
3. **健康追蹤**：分析你的運動和飲食數據，了解哪些習慣最有效

**為什麼{topic}重要？**
- 幫助我們做出更好的決定
- 避免被誤導性的信息欺騙
- 讓我們能夠看到數據背後的真實情況

即使你不是統計學家，理解{topic}的基本概念也能幫助你在日常生活中更好地理解世界和做出決策。沒有複雜的公式，只需要清晰的思考和基本的分析能力。
"""
        elif difficulty == "intermediate":
            return f"""【{level}難度】{topic}解釋

{topic}是統計學中的重要概念，用於分析和理解數據的特性和模式。

**定義與基本概念**：
{topic}提供了一種系統方法來組織、分析和解釋數據。它建立在概率論基礎上，允許我們從樣本數據推斷母體特徵。

**主要特點**：
1. 提供客觀的數據分析框架
2. 允許我們量化不確定性
3. 幫助識別數據中的模式和關係
4. 支持基於證據的決策過程

**應用領域**：
- **商業分析**：預測銷售趨勢、客戶行為分析
- **科學研究**：實驗設計與結果評估
- **醫學研究**：疾病風險因素分析、治療效果評估
- **社會科學**：人口趨勢分析、行為模式研究

**相關技術與方法**：
- 描述性統計：均值、中位數、標準差等
- 推論統計：置信區間、假設檢定
- 回歸分析：線性回歸、多變量回歸
- 分類方法：聚類分析、判別分析

**優勢與限制**：
優勢：
- 提供數據驅動的客觀見解
- 量化結果的準確性和可靠性
- 允許基於概率做出預測

限制：
- 依賴於數據質量和樣本代表性
- 可能受到統計假設的限制
- 結果解釋需要專業知識

掌握{topic}的基本原理和應用方法，能夠顯著提升數據分析能力和科學決策水平。
"""
        else:  # advanced
            return f"""【{level}難度】{topic}解釋

{topic}是統計學和數據科學的核心概念，它提供了嚴謹的數學框架用於數據分析、不確定性量化和統計推斷。

**理論基礎與數學框架**：
{topic}建立在測度論和概率論的基礎上，涉及隨機變量的分佈特性、矩估計、最大似然等高級統計原理。在形式上，可表示為參數空間Θ上的函數族{{f(x|θ): θ∈Θ}}，其中f代表概率密度或質量函數。

**高級方法論**：
1. **漸近理論**：建立在中心極限定理和大數定律基礎上，研究估計量的大樣本性質
2. **貝葉斯方法**：運用貝葉斯定理更新先驗分佈p(θ)至後驗分佈p(θ|x)
3. **非參數方法**：不假設特定分佈形式，如核密度估計、自助法(Bootstrap)
4. **穩健統計**：開發對異常值和分佈偏離不敏感的方法

**數學表達與推導**：
在{topic}的研究中，常用到的數學工具包括：
- 矩母函數：M_X(t) = E[e^{{tX}}]
- 充分統計量：基於Fisher-Neyman分解定理
- 指數族：f(x|θ) = h(x)c(θ)exp{{Σw_j(θ)t_j(x)}}
- 似然比檢定：λ = sup{{L(θ|x): θ∈Θ_0}}/sup{{L(θ|x): θ∈Θ}}

**高級應用領域**：
- **時間序列分析**：ARIMA模型、波動率建模、協整分析
- **多元分析**：主成分分析、因子分析、典型相關分析
- **機器學習交叉領域**：正則化方法、集成學習、統計學習理論
- **因果推斷**：潛在結果框架、工具變數法、傾向得分匹配

**方法論挑戰與前沿研究**：
1. **高維數據分析**：當p>>n時的估計與推斷
2. **計算統計學**：MCMC方法、變分推斷、近似貝葉斯計算
3. **複雜數據結構**：函數型數據、網絡數據、空間-時間數據
4. **缺失數據機制**：MAR、MCAR、MNAR的識別與處理

**統計哲學視角**：
{topic}涉及頻率學派與貝葉斯學派的深層哲學差異，前者關注長期頻率性質，後者基於主觀信念更新。近年來，兩派方法在實際應用中趨於融合，形成更為綜合的統計推斷框架。

掌握{topic}的高級理論和方法，需要深厚的數學基礎和統計學直覺，但能夠提供解決現代數據科學複雜問題的強大工具。
"""

    return explanation

def get_mock_practice_questions(topic, number, difficulty):
    """提供模擬的練習題"""
    difficulty_level = {"beginner": "基礎", "intermediate": "中級", "advanced": "高級"}
    level = difficulty_level.get(difficulty, "中級")
    
    if topic == "標準差":
        return f"""【{level}難度】標準差練習題

**練習題1：基本計算**
問題：計算以下數據集的樣本標準差：4, 8, 12, 16, 20
解答：
1. 首先計算平均值 μ = (4 + 8 + 12 + 16 + 20) / 5 = 12
2. 計算各數據與平均值的差的平方：
   (4-12)² = (-8)² = 64
   (8-12)² = (-4)² = 16
   (12-12)² = 0
   (16-12)² = 16
   (20-12)² = 64
3. 求這些平方差的平均值：(64 + 16 + 0 + 16 + 64) / 5 = 32
4. 取平方根：√32 = 5.66

因此，樣本標準差為 5.66。

**練習題2：應用理解**
問題：兩個班級的考試分數如下：
- A班：平均分75分，標準差5分
- B班：平均分75分，標準差15分
請解釋這兩個班級成績分佈的差異，並說明哪個班級的學生成績更為一致？

解答：
兩個班級的平均分都是75分，但標準差不同：
- A班標準差較小(5分)，表示大多數學生的分數都集中在平均分附近，成績分佈較為緊密。
- B班標準差較大(15分)，表示學生分數差異較大，分佈較為分散。

A班學生的成績更為一致，因為標準差小表示數據偏離平均值的程度小。若假設成績呈常態分佈，A班約68%的學生成績在70-80分之間，而B班約68%的學生成績在60-90分之間，範圍更廣。

**練習題3：實際情境分析**
問題：一家製藥公司測試兩種降血壓藥物，結果如下：
- 藥物A：平均降低血壓15mmHg，標準差2mmHg
- 藥物B：平均降低血壓17mmHg，標準差7mmHg
作為醫生，您會推薦哪種藥物？為什麼？

解答：
這個問題需要權衡效果與穩定性：
- 藥物A：平均降低15mmHg，標準差小(2mmHg)，表示效果較為穩定一致
- 藥物B：平均降低17mmHg，標準差大(7mmHg)，表示平均效果較好但個體間差異大

作為醫生，推薦哪種藥物取決於患者情況：
1. 對於需要可預測、穩定效果的患者（如老年人或有多種疾病的患者），藥物A可能更適合，因為其效果更為一致，減少不良反應或效果不足的風險。
2. 對於血壓顯著升高且能夠密切監測的患者，藥物B可能更有效。

總結來說，如果優先考慮治療穩定性，選擇藥物A；如果優先考慮平均效果，選擇藥物B。這展示了如何使用標準差來做出臨床決策。
"""
    else:
        # 模擬其他主題的練習題
        return f"""【{level}難度】{topic}練習題

**練習題1**
問題：關於{topic}的基本概念，以下哪一項描述是正確的？
A. 選項A
B. 選項B
C. 選項C
D. 選項D

解答：
正確答案是B。因為選項B準確描述了{topic}的核心特性，特別是在考慮統計應用時的基本原理。其他選項雖然部分正確，但不完整或有誤導性。

**練習題2**
問題：在應用{topic}時，常見的錯誤包括哪些？詳細解釋其中一個錯誤及其潛在後果。

解答：
應用{topic}時的常見錯誤包括：
1. 忽略數據分佈假設
2. 錯誤解讀結果
3. 不適當的樣本選擇

以錯誤解讀結果為例，這通常發生在研究者過度簡化{topic}提供的信息時。例如，僅關注單一統計值而忽略整體上下文，可能導致決策偏差。後果可能包括錯誤的研究結論或不當的資源分配。正確應用時，應結合多種統計指標和具體研究背景進行綜合判斷。

**練習題3**
問題：設計一個應用{topic}的研究方案，解決一個實際問題。包括研究問題、數據收集方法和分析策略。

解答：
研究問題：評估新教學方法對學生統計學理解的影響

數據收集方法：
- 選擇兩組相似背景的學生（實驗組和對照組）
- 實驗組使用新教學方法，對照組使用傳統方法
- 收集前測和後測成績數據
- 課程結束後進行滿意度調查

分析策略：
1. 使用{topic}分析兩組學生的前後測分數差異
2. 計算效應量以判斷教學方法的實際影響程度
3. 控制學生背景變量（如先前知識）進行條件分析
4. 結合量化和質性數據評估整體有效性

這個研究設計通過合理運用{topic}，可以客觀評估教學創新的實際效果，為教育決策提供科學依據。
"""

def get_mock_study_plan(topics, duration_weeks):
    """提供模擬的學習計劃數據，作為API不可用時的備用方案"""
    
    # 轉換主題列表為字符串，如果是列表的話
    if isinstance(topics, list):
        topics_str = ", ".join(topics)
    else:
        topics_str = topics
    
    # 標準化週數
    try:
        weeks = int(duration_weeks)
    except (ValueError, TypeError):
        weeks = 4
    
    # 創建模擬學習計劃
    mock_plan = {
        "overview": f"這是一個為期{weeks}週的統計學學習計劃，專注於以下主題：{topics_str}。本計劃旨在提供系統化的學習路徑，幫助您建立扎實的統計學基礎，並逐步掌握相關概念和應用技能。",
        "weeks": [],
        "resources": [
            {
                "title": "統計學導論 (第7版)",
                "description": "Richard D. De Veaux 等著，經典的統計學入門教材，涵蓋基礎概念和應用方法。"
            },
            {
                "title": "可汗學院統計學課程",
                "description": "免費在線視頻課程，提供直觀易懂的統計學概念講解。"
            },
            {
                "title": "R統計軟體 / Python with Pandas",
                "description": "推薦學習這些工具以進行實際數據分析和統計計算。"
            }
        ]
    }
    
    # 生成每週的計劃
    for week in range(1, weeks + 1):
        # 為不同週創建不同的主題內容
        if "描述統計" in topics_str or week <= weeks/3:
            focus = "基礎概念與描述統計"
            weekly_topics = ["資料類型與測量尺度", "集中趨勢測量", "離散程度測量"]
            activities = ["閱讀教材第1-3章", "完成10個練習題", "使用Excel或R計算基本統計量"]
        elif "機率" in topics_str or week <= 2*weeks/3:
            focus = "機率與隨機變數"
            weekly_topics = ["基本機率概念", "條件機率", "離散與連續隨機變量"]
            activities = ["閱讀教材第4-6章", "完成機率習題集", "嘗試解決貝氏定理問題"]
        else:
            focus = "統計推論與假設檢定"
            weekly_topics = ["抽樣分佈", "信賴區間估計", "假設檢定流程"]
            activities = ["閱讀教材第7-9章", "完成t檢定實作", "分析真實數據集並撰寫報告"]
        
        week_plan = {
            "title": f"第{week}週：統計學基礎 (第{week}部分)",
            "focus": focus,
            "description": f"本週將專注於{focus}的學習。通過課本閱讀與實踐練習，掌握核心概念並學會應用。",
            "topics": weekly_topics,
            "activities": activities
        }
        
        mock_plan["weeks"].append(week_plan)
    
    return mock_plan

def get_smart_mock_response(message):
    """
    生成智能模擬回答 - 當API不可用時使用
    為不同統計學問題提供詳細專業解答
    """
    print("生成智能模擬回答...")
    
    # 將用戶消息轉為小寫以便匹配
    message_lower = message.lower()
    
    # ===== 基礎統計學概念解釋 =====
    
    # 母體與樣本
    if any(keyword in message_lower for keyword in ["母體", "總體", "population"]):
        if "參數" in message_lower:
            return """
在統計學中，母體參數是描述整個研究對象總體特徵的數值。

主要母體參數包括：
1. 母體平均數(μ)：表示總體中所有值的平均水平
2. 母體變異數(σ²)：表示數據分散程度的平方度量
3. 母體標準差(σ)：表示數據分散程度，為變異數的平方根
4. 母體比例(p)：表示具有特定特徵個體在總體中的比例

母體指的是研究者感興趣的完整資料集合，通常因為規模太大或無法完全取得而需要通過抽樣來研究。例如：
- 一個國家所有居民的收入（母體）
- 一所大學所有學生的GPA（母體）
- 一個製造過程產出的所有產品（母體）

統計推論的核心目標是通過樣本統計量（如樣本平均數x̄）來推斷母體參數（如μ）。第8章「點估計與區間估計」詳細討論了這個過程。
"""
        
        if "樣本" in message_lower:
            return """
在統計學中，樣本與母體是兩個核心概念：

**母體**：研究者感興趣的完整資料集合，通常無法完全獲取或測量。
**樣本**：從母體中抽取的一部分個體，用於研究和分析。

樣本與母體的關係：
1. 樣本是母體的子集
2. 良好的樣本應該代表母體的特徵（有代表性）
3. 隨機抽樣可以減少偏差，提高樣本代表性

當我們計算樣本的特徵時，得到的是統計量（statistics）：
- 樣本平均數(x̄)
- 樣本標準差(s)
- 樣本比例(p̂)

這些統計量用於估計相應的母體參數（parameters）：
- 母體平均數(μ)
- 母體標準差(σ)
- 母體比例(p)

在課程第2章「資料整理與統計量」中有詳細介紹樣本統計量的計算，第8章則討論如何用樣本統計量推斷母體參數。
"""
    
    # 描述統計與推論統計
    if any(keyword in message_lower for keyword in ["描述統計", "descriptive"]):
        return """
描述統計（Descriptive Statistics）是統計學的基礎分支，專注於組織、匯總和呈現資料集的特徵，不進行推論或預測。

描述統計的主要內容包括：

1. 集中趨勢測量：
   - 平均數（Mean）：資料的算術平均
   - 中位數（Median）：排序後的中間值
   - 眾數（Mode）：出現頻率最高的值

2. 離散程度測量：
   - 範圍（Range）：最大值減最小值
   - 標準差（Standard Deviation）：測量資料偏離平均數的程度
   - 變異數（Variance）：標準差的平方
   - 四分位距（Interquartile Range）：第三四分位數減第一四分位數

3. 分佈特徵：
   - 偏態（Skewness）：分佈的不對稱程度
   - 峰度（Kurtosis）：分佈的「尖峭度」

4. 資料視覺化：
   - 直方圖（Histogram）
   - 箱形圖（Box Plot）
   - 散點圖（Scatter Plot）
   - 條形圖（Bar Chart）

描述統計在課程的第2-4章有詳細介紹，是統計分析的第一步，也是進行推論統計的基礎。
"""
    
    if any(keyword in message_lower for keyword in ["推論統計", "inferential"]):
        return """
推論統計（Inferential Statistics）是統計學的核心分支，目的是從樣本數據推斷總體特徵並進行科學決策。

推論統計的主要內容包括：

1. 抽樣理論：
   - 抽樣分配（Sampling Distribution）
   - 中央極限定理（Central Limit Theorem）
   - 標準誤（Standard Error）

2. 參數估計：
   - 點估計（Point Estimation）：提供單一最佳估計值
   - 區間估計（Interval Estimation）：提供可能範圍，如信賴區間

3. 假設檢定：
   - 虛無假設與對立假設（H₀ vs H₁）
   - 顯著水準與p值
   - 第一類錯誤與第二類錯誤

4. 各類統計檢定：
   - t檢定（單一樣本、獨立樣本、配對樣本）
   - 卡方檢定
   - 變異數分析（ANOVA）
   - 非參數檢定

推論統計是進階的統計分析方法，在課程的第7-16章有詳細介紹，它建立在描述統計和機率理論的基礎上，是實證研究得出結論的關鍵工具。
"""
    
    # 機率與分佈
    if any(keyword in message_lower for keyword in ["機率", "概率", "probability"]):
        return """
機率（Probability）是度量事件發生可能性的數學工具，是統計學的理論基礎。

機率的核心概念：

1. 基本定義：
   - 古典定義：理想情況下，有利事件數除以可能事件總數
   - 頻率定義：長期試驗中事件發生的相對頻率
   - 公理化定義：滿足kolmogorov公理系統的測度

2. 機率法則：
   - 加法法則：P(A或B) = P(A) + P(B) - P(A且B)
   - 乘法法則：P(A且B) = P(A) × P(B|A)
   - 條件機率：P(B|A) = P(A且B) / P(A)

3. 隨機變數：
   - 離散隨機變數
   - 連續隨機變數
   - 期望值與變異數

4. 常見分配：
   - 二項分配（離散）：n次獨立試驗中，成功k次的機率
   - 常態分配（連續）：自然界中最常見的分配
   - t分配、卡方分配、F分配等

機率理論是統計推論的數學基礎，在課程的第5-7章有詳細介紹。掌握機率理論對理解假設檢定、信賴區間等後續內容至關重要。
"""
    
    if any(keyword in message_lower for keyword in ["分佈", "分配", "distribution"]):
        return """
機率分配（Probability Distribution）描述隨機變數可能取值及其機率的數學模型，是統計學的核心概念。

常見的機率分配：

1. 離散機率分配：
   - 二項分配（Binomial）：適用於成功/失敗的n次獨立試驗
   - 泊松分配（Poisson）：適用於在固定時間或空間內發生的隨機事件
   - 幾何分配（Geometric）：直到首次成功所需的試驗次數
   - 超幾何分配（Hypergeometric）：不放回抽樣的情況

2. 連續機率分配：
   - 常態分配（Normal）：最重要的連續分配，鐘形曲線
   - 均勻分配（Uniform）：在特定區間內的值出現機率相等
   - 指數分配（Exponential）：事件之間的等待時間
   - t分配：樣本量小時用於推論母體平均數
   - 卡方分配：變異數分析、適合度檢定
   - F分配：比較兩個變異數

3. 分配特性：
   - 期望值（Expected Value）：分配的中心位置
   - 變異數（Variance）：分散程度
   - 偏態（Skewness）：不對稱程度
   - 峰度（Kurtosis）：尾部厚度

4. 應用領域：
   - 抽樣理論：樣本統計量的抽樣分配
   - 假設檢定：檢定統計量的分配
   - 信賴區間：參數估計的不確定性

課程第6-7章詳細介紹了這些分配及其應用，理解這些概念對統計推論至關重要。
"""
    
    # 假設檢定
    if any(keyword in message_lower for keyword in ["假設檢定", "hypothesis", "檢定"]):
        return """
假設檢定（Hypothesis Testing）是統計學中用於評估關於總體參數的假設是否成立的系統方法。

假設檢定的基本步驟：

1. 提出假設：
   - 虛無假設H₀：預設為真的陳述（通常表示「無效果」或「無差異」）
   - 對立假設H₁：研究者希望證明的陳述

2. 選擇顯著水準(α)：
   - 通常為0.05或0.01
   - 代表願意接受的第一類錯誤（拒絕實際上正確的H₀）機率

3. 收集數據並計算檢定統計量：
   - z值、t值、F值或χ²值等，取決於檢定類型

4. 計算p值或臨界值：
   - p值：觀察到的數據（或更極端）在H₀為真時出現的機率
   - 臨界值：決定拒絕區域的邊界

5. 做出決策：
   - 若p值 < α，則拒絕H₀
   - 若p值 ≥ α，則不拒絕H₀

6. 解釋結果：
   - 統計顯著性的含義
   - 效應量的大小
   - 實際應用意義

常見的假設檢定類型：
- 單一樣本t檢定：比較樣本平均數與已知總體平均數
- 獨立樣本t檢定：比較兩個獨立樣本的平均數
- 配對樣本t檢定：比較相關樣本的平均數
- 變異數分析（ANOVA）：比較多個群組的平均數
- 卡方檢定：分析分類變項之間的關係

課程的第9-11章詳細介紹了各種假設檢定方法及其應用。
"""
    
    # 標準差與變異數
    if any(keyword in message_lower for keyword in ["標準差", "變異", "變異數", "標準偏差", "standard deviation", "variance"]):
        return """
標準差與變異數是統計學中兩個密切相關的分散測度，用於量化數據的離散程度。

變異數（Variance）：
- 定義：各觀測值與平均數差異平方的平均
- 母體變異數公式：σ² = Σ(X - μ)² / N
- 樣本變異數公式：s² = Σ(X - x̄)² / (n-1)
- 單位：原始數據單位的平方（如：若數據單位是公尺，變異數單位是平方公尺）

標準差（Standard Deviation）：
- 定義：變異數的平方根
- 母體標準差公式：σ = √σ²
- 樣本標準差公式：s = √s²
- 單位：與原始數據相同（如公尺）

兩者的主要區別：
1. 標準差與原始數據單位相同，更容易直觀理解
2. 變異數在數學運算中具有良好的性質（如可加性），常用於進階統計分析
3. 標準差受極端值影響較小，變異數對極端值更敏感
4. 在正態分佈中，約68%的數據落在平均數±1個標準差的範圍內

實際應用：
- 標準差常用於描述數據的分散程度和計算Z分數
- 變異數是許多統計程序的基礎，如ANOVA和回歸分析
- 兩者都可用於比較不同數據集的變異性

課程第3章詳細介紹了這些概念及其計算方法。
"""
    
    # 顯著性與p值
    if any(keyword in message_lower for keyword in ["顯著", "p值", "p-value", "significant"]):
        return """
統計顯著性和p值是假設檢定中的核心概念，用於評估結果的可信度。

p值（p-value）：
- 定義：在虛無假設為真的條件下，觀察到當前或更極端結果的機率
- 解釋：p值越小，表示數據與虛無假設越不相容
- 範圍：0到1之間的數值

顯著水準（Significance Level，α）：
- 定義：研究者事先設定的閾值，通常為0.05或0.01
- 意義：願意接受的第一類錯誤（誤拒虛無假設）機率
- 決策規則：當p值 < α時，結果被視為「統計顯著」

統計顯著性的含義：
- 「統計顯著」表示觀察到的結果不太可能是偶然發生的
- 不代表結果具有實質意義或重要性
- 不表示效應的大小或實際影響

p值的正確解讀：
- p值不是虛無假設為真的機率
- p值不能直接用來比較不同研究的重要性
- p值受樣本大小影響，大樣本容易得到顯著結果

統計顯著性的常見誤解：
- 混淆統計顯著性與實際重要性
- 將「未能拒絕虛無假設」解讀為「證明虛無假設」
- 過度關注p<0.05的二分法思維，忽視效應量

課程第9章詳細討論了p值的計算與解釋，第10-11章應用於各類假設檢定中。
"""
    
    # 回歸分析
    if any(keyword in message_lower for keyword in ["回歸", "迴歸", "regression"]):
        return """
回歸分析是統計學中用於探究變數之間關係的強大工具，特別是預測一個因變數基於一個或多個自變數的值。

線性回歸的基本形式：

1. 簡單線性回歸：
   - 模型：Y = β₀ + β₁X + ε
   - Y：因變數（被預測變數）
   - X：自變數（預測變數）
   - β₀：截距
   - β₁：斜率係數
   - ε：誤差項

2. 多元線性回歸：
   - 模型：Y = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ + ε
   - 包含多個自變數X₁, X₂, ..., Xₖ

回歸分析的關鍵概念：

1. 參數估計：
   - 最小平方法（OLS）：最小化殘差平方和
   - 最大似然估計：在特定分佈假設下

2. 模型評估：
   - 決定係數R²：模型解釋的變異比例
   - 調整後R²：考慮自變數數量的修正版R²
   - F檢定：整體模型的顯著性
   - t檢定：個別係數的顯著性

3. 診斷檢查：
   - 殘差分析：檢查常態性、同質性等假設
   - 多重共線性：自變數間的高度相關性
   - 影響點：對模型估計有顯著影響的觀測值

4. 進階回歸技術：
   - Logistic回歸：處理二分類因變數
   - 多項式回歸：非線性關係的線性模型表示
   - 分段回歸：處理不同區域有不同斜率的情況

回歸分析在第12-13章有詳細介紹，是預測分析、因果推論和科學建模的基礎工具。
"""
    
    # 相關分析
    if any(keyword in message_lower for keyword in ["相關", "correlation"]):
        return """
相關分析是研究兩個變數之間線性關係強度和方向的統計方法，是探索性數據分析和回歸分析的重要前置步驟。

皮爾森相關係數（Pearson Correlation Coefficient）：
- 符號：r
- 範圍：-1到+1之間
- 解釋：
  * r = +1：完美正相關
  * r = -1：完美負相關
  * r = 0：無線性相關
  * 0<|r|<0.3：弱相關
  * 0.3≤|r|<0.7：中等相關
  * 0.7≤|r|<1：強相關
- 計算公式：r = Σ[(X-x̄)(Y-ȳ)] / √[Σ(X-x̄)²·Σ(Y-ȳ)²]

其他相關係數：
- 斯皮爾曼等級相關係數（Spearman's Rank Correlation）：適用於非參數或順序資料
- 點二系列相關（Point-Biserial Correlation）：連續變數與二分變數間的相關
- 偏相關（Partial Correlation）：控制第三變數影響的相關

相關分析的關鍵特性：
1. 相關不等於因果：相關關係不能證明因果關係
2. 受極端值影響：離群值可能顯著改變相關係數
3. 只測量線性關係：無法捕捉非線性關係
4. 對尺度敏感：變數的變換可能改變相關強度

相關分析的實際應用：
- 預測分析的前置步驟：識別潛在有價值的預測變數
- 多重共線性檢查：評估自變數間的相關性
- 構念效度分析：評估測量工具的一致性
- 探索性研究：發現變數之間可能的關係模式

課程第12章詳細介紹了相關分析的原理與應用。
"""

    # 常見統計概念
    if any(keyword in message_lower for keyword in ["常態", "正態", "normal"]):
        return """
常態分配（Normal Distribution），也稱為高斯分配，是統計學中最重要的概率分配，其特徵性的鐘形曲線在自然和社會現象中普遍存在。

常態分配的數學特性：
- 概率密度函數：f(x) = (1/σ√2π)e^(-(x-μ)²/2σ²)
- 由兩個參數完全確定：
  * 平均數μ：分配的中心位置
  * 標準差σ：分配的寬度或分散程度
- 標準常態分配（Z分配）：μ=0，σ=1

常態分配的主要特徵：
1. 對稱性：以平均數為中心對稱
2. 平均數、中位數、眾數三者相等
3. 68-95-99.7法則：
   - 約68%的數據落在μ±1σ範圍內
   - 約95%的數據落在μ±2σ範圍內
   - 約99.7%的數據落在μ±3σ範圍內
4. 尾部迅速衰減但永不為零

常態分配的重要性：
- 中央極限定理：大樣本的樣本平均數趨向常態分配
- 許多統計檢定基於常態性假設
- 許多自然和社會現象近似遵循常態分配
- 便於數學處理和理論推導

常態分配在統計學中的應用：
- Z分數標準化：將不同尺度的數據轉換為可比較的形式
- 參數估計：許多估計量在大樣本下近似常態分配
- 假設檢定：如t檢定、Z檢定等
- 機率計算：利用標準常態表計算機率

課程第6章詳細介紹了常態分配的性質和應用。
"""

    if any(keyword in message_lower for keyword in ["區間估計", "信賴區間", "confidence"]):
        return """
區間估計與信賴區間是統計推論中用於估計母體參數可能值範圍的方法，比單一點估計提供更多資訊。

信賴區間的基本概念：
- 定義：以特定信賴水準（如95%）包含真實母體參數的區間
- 形式：[點估計 - 誤差界限, 點估計 + 誤差界限]
- 解釋：如果重複抽樣多次，約95%的信賴區間會包含真實參數值

常見的信賴區間類型：

1. 母體平均數的信賴區間：
   - 已知σ時：x̄ ± zα/2·(σ/√n)
   - 未知σ時：x̄ ± tα/2·(s/√n)，自由度=n-1
   - 大樣本時（n≥30）：近似使用z分配

2. 母體比例的信賴區間：
   - p̂ ± zα/2·√[p̂(1-p̂)/n]
   - 適用條件：np̂≥5且n(1-p̂)≥5

3. 母體變異數的信賴區間：
   - 基於卡方分配：[(n-1)s²/χ²α/2, (n-1)s²/χ²1-α/2]

信賴區間的影響因素：

1. 信賴水準（1-α）：
   - 增加信賴水準會擴大區間寬度
   - 常用水準：90%、95%、99%

2. 樣本大小(n)：
   - 增加樣本大小會縮小區間寬度
   - 區間寬度與√n成反比

3. 樣本變異性(s)：
   - 數據變異性越大，區間越寬
   - 反映估計的不確定性

信賴區間的常見誤解：
- 誤解：95%信賴區間表示母體參數有95%的機率落在此區間內
- 正確：母體參數是固定的，區間是隨機的；95%指的是重複抽樣下區間包含參數的比例

課程第8章詳細介紹了區間估計的原理與應用。
"""

    # 如果沒有匹配到任何關鍵詞，提供更友好的回應
    greetings = ["你好", "哈囉", "嗨", "您好", "hello", "hi"]
    if any(greeting in message_lower for greeting in greetings):
        return """你好！我是統計學助手，很高興能幫助你解答統計學方面的問題。你可以詢問我關於描述統計、機率分布、假設檢定、回歸分析等統計學概念或方法。請告訴我你想了解的具體統計學問題。"""
    
    if len(message_lower) < 10:
        return """您的提問似乎有點簡短。為了提供準確的統計學解答，請詳細描述您的問題或疑惑。您可以詢問特定的統計概念、方法或應用。我可以解答關於描述統計、機率理論、假設檢定、回歸分析等統計學主題的問題。"""
    
    # 一般回應
    return """我理解您想詢問關於統計學的問題。請提供更具體的資訊，例如：

1. 您想了解哪個統計學概念的定義或解釋？（如「什麼是t檢定？」）
2. 您需要了解某個統計方法的應用場景嗎？（如「何時使用卡方檢定？」） 
3. 您想了解如何分析特定類型的數據嗎？（如「如何分析配對樣本數據？」）
4. 您對統計學中的哪個領域特別感興趣？（如「描述統計」或「推論統計」）

提供更多細節後，我可以給您更準確的統計學知識解答。"""

def get_api_status():
    """獲取當前API連接狀態"""
    return API_STATUS

def update_api_config(api_key, api_base):
    """更新API配置並測試連接"""
    return test_api_connection(api_key, api_base)

def chat_with_assistant(message, history=None):
    """與AI助手聊天，使用聊天歷史記錄進行上下文處理"""
    print(f"[chat_with_assistant] Received message: {message}")
    
    # 確保歷史記錄是一個列表
    if history is None:
        history = []
    
    try:
        # 應用測試模式
        if app.config.get('TESTING', False) or not is_client_initialized():
            print("[chat_with_assistant] Running in test mode or client not initialized")
            return {
                "success": True,
                "answer": "這是一個測試回答，實際聊天功能需要設定API金鑰。",
                "full_response": None
            }
        
        print(f"[chat_with_assistant] Processing message with history length: {len(history)}")
        
        # 構建消息列表
        messages = [
            {"role": "system", "content": "你是一個專業的統計學教師助手，專門協助學生解決統計學問題和提供相關學術指導。請提供準確、專業且容易理解的回答。"},
        ]
        
        # 添加歷史記錄
        for entry in history:
            if 'role' in entry and 'content' in entry:
                messages.append({"role": entry['role'], "content": entry['content']})
            else:
                print(f"[chat_with_assistant] Warning: Invalid history entry format: {entry}")
        
        # 添加當前消息
        messages.append({"role": "user", "content": message})
        
        print(f"[chat_with_assistant] Sending {len(messages)} messages to API")
        
        # 調用API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        
        if response and hasattr(response, 'choices') and len(response.choices) > 0:
            answer = response.choices[0].message.content
            print(f"[chat_with_assistant] Got response from API, length: {len(answer) if answer else 0}")
            return {
                "success": True,
                "answer": answer,
                "full_response": response
            }
        else:
            print("[chat_with_assistant] Error: Empty or invalid API response")
            return {
                "success": False,
                "error": "無法從AI助手獲取回覆",
                "details": "API返回的響應無效或為空"
            }
    
    except Exception as e:
        print(f"[chat_with_assistant] Exception occurred: {str(e)}")
        return {
            "success": False,
            "error": "處理聊天訊息時發生錯誤",
            "details": str(e)
        }

def is_client_initialized():
    """檢查API客戶端是否已初始化"""
    global client
    return client is not None