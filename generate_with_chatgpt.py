import json
import os
import requests
import time
import random

# API設定
OPENAI_API_KEY = "sk-uYf5DnpjM2xaHE1p261310C081E94d5a8aF0D61cE3F6Bf68"
OPENAI_API_BASE = "https://free.v36.cm"

def generate_content_with_chatgpt(prompt, system_prompt="", max_retries=3, timeout=30):
    """
    使用ChatGPT API生成內容，增加重試機制和超時設置
    
    參數:
        prompt (str): 用戶提示
        system_prompt (str): 系統提示
        max_retries (int): 最大重試次數
        timeout (int): 請求超時時間（秒）
    
    返回:
        str: 生成的內容
    """
    retry_count = 0
    backoff_time = 2  # 初始重試等待時間（秒）
    
    while retry_count < max_retries:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [],
                "temperature": 0.7,
                "max_tokens": 2000  # 减少令牌数以降低超时风险
            }
            
            if system_prompt:
                data["messages"].append({"role": "system", "content": system_prompt})
            
            data["messages"].append({"role": "user", "content": prompt})
            
            print(f"正在發送API請求... (嘗試 {retry_count + 1}/{max_retries})")
            response = requests.post(
                f"{OPENAI_API_BASE}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout  # 設置請求超時
            )
            
            if response.status_code == 200:
                response_json = response.json()
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    print("API請求成功！")
                    return response_json["choices"][0]["message"]["content"]
                else:
                    print(f"API返回無效響應: {response_json}")
            elif response.status_code == 429:  # 速率限制
                print(f"API速率限制，等待後重試...")
                time.sleep(backoff_time + random.uniform(0, 1))
                backoff_time *= 2  # 指數退避
                retry_count += 1
                continue
            elif response.status_code >= 500:  # 服務器錯誤
                print(f"API服務器錯誤 (狀態碼: {response.status_code})，重試中...")
                time.sleep(backoff_time + random.uniform(0, 1))
                backoff_time *= 2
                retry_count += 1
                continue
            else:
                print(f"API請求失敗 (狀態碼: {response.status_code}): {response.text}")
        
        except requests.exceptions.Timeout:
            print(f"API請求超時，重試中...")
            time.sleep(backoff_time + random.uniform(0, 1))
            backoff_time *= 2
            retry_count += 1
            continue
        except Exception as e:
            print(f"生成內容時出錯: {str(e)}")
        
        # 如果代碼執行到這裡，表示請求失敗且不符合重試條件，或所有重試都失敗了
        break
    
    print("API請求失敗，使用默認內容")
    return ""

# 使用更簡短的內容，降低API負擔
def get_minimal_content(section_title, chapter_title):
    """為節省API負擔，生成最小化的講義內容"""
    return f"""=== 主要內容 ===
{section_title}是{chapter_title}中的重要概念。它幫助我們理解統計學的基本原理和應用方法。學習{section_title}對掌握統計學知識體系有重要意義。

=== 實際應用例子 ===
1. {section_title}在商業分析中的應用
2. {section_title}在科學研究中的應用
3. {section_title}在日常生活中的應用

=== 記憶技巧 ===
1. 使用首字母縮寫記憶{section_title}的關鍵概念
2. 將{section_title}與熟悉的生活情境聯繫起來

=== 練習題 ===
問題1: 請簡述{section_title}的基本概念。
答案1: {section_title}是{chapter_title}中的基本概念，主要涉及數據的收集、整理和分析。

問題2: {section_title}在實際應用中有哪些例子？
答案2: {section_title}在市場研究、科學實驗和教育評估等領域有廣泛應用。

問題3: {section_title}與其他統計概念有什麼關聯？
答案3: {section_title}與數據分析、假設檢驗等概念密切相關，共同構成統計學的知識體系。"""

def generate_section_content(section_title, chapter_title="統計學", difficulty="intermediate", use_minimal=False):
    """
    生成講義小節內容
    
    參數:
        section_title (str): 小節標題
        chapter_title (str): 章節標題
        difficulty (str): 難度級別
        use_minimal (bool): 是否使用最小化內容 (API失敗時)
    
    返回:
        dict: 包含生成的內容、例子、記憶技巧和練習題
    """
    # 構建系統提示 (簡化)
    system_prompt = f"""你是專業統計學教授，請為《{chapter_title}》中的「{section_title}」小節生成內容，
包含主要概念解釋、應用例子、記憶技巧和練習題。"""
    
    # 構建用戶提示 (簡化)
    user_prompt = f"""請為統計學講義生成「{section_title}」小節的詳細內容，使用以下格式：

=== 主要內容 ===
(簡潔清楚的概念解釋，500-800字)

=== 實際應用例子 ===
1. (第一個例子)
2. (第二個例子)
3. (第三個例子)

=== 記憶技巧 ===
1. (第一個技巧)
2. (第二個技巧)

=== 練習題 ===
問題1: (第一個問題)
答案1: (第一個答案)

問題2: (第二個問題)
答案2: (第二個答案)

問題3: (第三個問題)
答案3: (第三個答案)"""
    
    # 如果要求使用最小化內容，則直接返回
    if use_minimal:
        content = get_minimal_content(section_title, chapter_title)
    else:
        # 嘗試使用ChatGPT生成內容
        content = generate_content_with_chatgpt(user_prompt, system_prompt)
        
        # 如果API失敗，使用最小化內容
        if not content:
            content = get_minimal_content(section_title, chapter_title)
    
    # 構建默認內容
    default_content = {
        "content": f"{section_title}是統計學中的重要概念，它幫助我們理解數據的本質和規律。{section_title}的應用廣泛，從基礎數據分析到複雜的統計推斷都有其重要作用。",
        "examples": [
            f"{section_title}在市場研究中的應用案例",
            f"{section_title}在醫學研究中的實際運用",
            f"{section_title}如何幫助企業做出更好的決策"
        ],
        "mnemonics": [
            f"記憶{section_title}的核心概念：將主要元素首字母組成有意義的詞組",
            f"通過類比法理解{section_title}：將抽象概念與日常生活情境連結"
        ],
        "exercises": [
            {
                "type": "short_answer",
                "question": f"請解釋{section_title}的基本概念及其重要性。",
                "answer": f"{section_title}是統計學的重要組成部分，它的核心在於幫助我們從數據中獲取有價值的信息。"
            },
            {
                "type": "short_answer",
                "question": f"描述{section_title}的一個實際應用場景。",
                "answer": f"在市場研究中，研究人員可以使用{section_title}來分析消費者行為模式，預測市場趨勢。"
            },
            {
                "type": "short_answer",
                "question": f"{section_title}與相關統計概念有什麼關係？",
                "answer": f"{section_title}與其他統計概念如數據收集、假設檢驗等緊密相連，共同構成完整的統計分析框架。"
            }
        ]
    }
    
    try:
        # 解析生成的內容
        parsed_content = {}
        
        # 解析主要內容
        if "=== 主要內容 ===" in content and "=== 實際應用例子 ===" in content:
            main_content = content.split("=== 主要內容 ===")[1].split("=== 實際應用例子 ===")[0].strip()
            parsed_content["content"] = main_content
        
        # 解析實際應用例子
        if "=== 實際應用例子 ===" in content and "=== 記憶技巧 ===" in content:
            examples_text = content.split("=== 實際應用例子 ===")[1].split("=== 記憶技巧 ===")[0].strip()
            examples = []
            for line in examples_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("==="):
                    # 移除數字前綴
                    if line[0].isdigit() and ". " in line:
                        examples.append(line.split(". ", 1)[1])
                    else:
                        examples.append(line)
            
            if examples:
                parsed_content["examples"] = examples[:3]  # 最多3個例子
        
        # 解析記憶技巧
        if "=== 記憶技巧 ===" in content and "=== 練習題 ===" in content:
            mnemonics_text = content.split("=== 記憶技巧 ===")[1].split("=== 練習題 ===")[0].strip()
            mnemonics = []
            for line in mnemonics_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("==="):
                    # 移除數字前綴
                    if line[0].isdigit() and ". " in line:
                        mnemonics.append(line.split(". ", 1)[1])
                    else:
                        mnemonics.append(line)
            
            if mnemonics:
                parsed_content["mnemonics"] = mnemonics[:2]  # 最多2個技巧
        
        # 解析練習題
        if "=== 練習題 ===" in content:
            exercises_text = content.split("=== 練習題 ===")[1].strip()
            exercises = []
            
            # 使用關鍵字分割
            parts = exercises_text.split("問題")
            for part in parts[1:]:  # 跳過第一個空元素
                if "答案" in part:
                    question_part = part.split("答案")[0]
                    answer_part = part.split("答案")[1]
                    
                    # 清理問題
                    question = question_part.strip()
                    if ":" in question:
                        question = question.split(":", 1)[1].strip()
                    
                    # 清理答案
                    answer = answer_part.strip()
                    if ":" in answer:
                        answer = answer.split(":", 1)[1].strip()
                    
                    # 移除數字前綴
                    if question and question[0].isdigit() and ". " in question:
                        question = question.split(". ", 1)[1]
                    if answer and answer[0].isdigit() and ". " in answer:
                        answer = answer.split(". ", 1)[1]
                    
                    # 找到下一個問題的位置
                    if "問題" in answer:
                        answer = answer.split("問題")[0].strip()
                    
                    exercises.append({
                        "type": "short_answer",
                        "question": question,
                        "answer": answer
                    })
            
            if exercises:
                parsed_content["exercises"] = exercises[:3]  # 最多3個練習題
        
        # 更新默認內容
        for key, value in parsed_content.items():
            if value:  # 只更新非空值
                default_content[key] = value
        
        return default_content
    
    except Exception as e:
        print(f"解析內容時出錯: {str(e)}")
        return default_content

def generate_chapter_content(chapter_number, chapter_title, sections):
    """
    生成完整章節的內容
    
    參數:
        chapter_number (int): 章節編號
        chapter_title (str): 章節標題
        sections (list): 小節標題列表
    
    返回:
        dict: 章節的完整內容
    """
    chapter = {
        "chapterNumber": str(chapter_number),
        "chapterTitle": chapter_title,
        "overview": f"本章介紹{chapter_title}的核心概念與應用，幫助學生掌握統計學的基礎知識並應用於實際問題分析。",
        "sections": []
    }
    
    # 跟踪API失敗計數
    api_failures = 0
    use_minimal = False  # 初始設置為不使用最小化內容
    
    for i, section_title in enumerate(sections):
        section_number = f"{chapter_number}.{i+1}"
        print(f"正在生成小節 {section_number}: {section_title}...")
        
        # 如果連續API失敗超過2次，切換到最小化模式
        if api_failures > 2:
            use_minimal = True
            print("切換到最小化內容模式")
        
        try:
            section_content = generate_section_content(section_title, chapter_title, use_minimal=use_minimal)
            # 如果成功生成，重置失敗計數
            if not use_minimal:
                api_failures = 0
        except Exception as e:
            print(f"生成小節內容時出錯: {str(e)}")
            api_failures += 1
            # 使用默認內容
            section_content = {
                "content": f"{section_title}是統計學中的重要概念，幫助理解數據分析的核心原理。",
                "examples": [f"{section_title}的應用例子"],
                "mnemonics": [f"{section_title}的記憶技巧"],
                "exercises": [
                    {
                        "type": "short_answer",
                        "question": f"請簡述{section_title}的基本概念",
                        "answer": f"{section_title}是統計學的重要組成部分。"
                    }
                ]
            }
        
        section = {
            "sectionNumber": section_number,
            "sectionTitle": section_title,
            "content": section_content["content"],
            "examples": section_content["examples"],
            "visuals": [
                {
                    "path": f"/static/images/ch{chapter_number}/{chapter_number}_{i+1}.png",
                    "description": f"{section_title}的圖解"
                }
            ],
            "mnemonics": section_content["mnemonics"],
            "exercises": section_content["exercises"]
        }
        
        chapter["sections"].append(section)
        
        # 添加間隔，避免API限制
        if not use_minimal:
            time.sleep(1 + random.uniform(0, 1))
    
    return chapter

def create_lecture_file(chapter, filename):
    """
    創建講義文件
    
    參數:
        chapter (dict): 章節內容
        filename (str): 文件名稱
    """
    data = {
        "courseTitle": "大學統計學",
        "version": "1.0",
        "chapters": [chapter]
    }
    
    # 確保目錄存在
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已創建講義文件: {filename}")

def generate_specific_chapter(chapter_num, chapter_title, sections):
    """
    生成特定章節內容並保存
    
    參數:
        chapter_num (int): 章節編號
        chapter_title (str): 章節標題
        sections (list): 小節標題列表
    """
    print(f"\n===== 正在生成第{chapter_num}章：{chapter_title} =====")
    
    chapter = generate_chapter_content(chapter_num, chapter_title, sections)
    
    lecture_dir = "講義"
    if not os.path.exists(lecture_dir):
        os.makedirs(lecture_dir)
    
    output_filename = os.path.join(lecture_dir, f"第{chapter_num}章_完整.json")
    create_lecture_file(chapter, output_filename)
    
    print(f"===== 完成第{chapter_num}章生成 =====\n")

# 示例使用
if __name__ == "__main__":
    # 測試單個小節生成
    content = generate_section_content("統計學的定義與範疇", "統計學簡介與基本概念")
    print("生成的內容示例：")
    print(f"內容長度: {len(content['content'])} 字符")
    print(f"例子數量: {len(content['examples'])}")
    print(f"記憶技巧數量: {len(content['mnemonics'])}")
    print(f"練習題數量: {len(content['exercises'])}")
    
    # 生成第一章
    generate_specific_chapter(
        1, 
        "統計學簡介與基本概念", 
        [
            "統計學的定義與範疇",
            "母體與樣本",
            "資料類型與測量尺度",
            "描述統計與推論統計",
            "統計研究設計流程",
            "資料收集方法",
            "統計學的歷史發展與應用"
        ]
    ) 