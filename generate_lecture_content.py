import json
import os
from ai_helper import client

def generate_section_content(section_title, chapter_title="統計學", difficulty="intermediate"):
    """
    使用ChatGPT生成統計學講義的章節內容
    
    參數:
        section_title (str): 小節標題
        chapter_title (str): 章節標題
        difficulty (str): 難度級別 (beginner, intermediate, advanced)
    
    返回:
        dict: 包含生成的內容、例子、記憶技巧和練習題
    """
    try:
        # 構建提示
        system_prompt = f"""你是一位專業的統計學教授，專長於設計易於理解且引人入勝的教材。
請使用以下心理學學習原則來設計教材：
1. 認知負荷理論：將複雜概念分解為易於理解的小部分
2. 情境學習：提供與實際生活相關的例子
3. 間隔重複：包含複習要點和記憶技巧
4. 多感官學習：提供視覺化描述和具體示例
5. 故事化教學：以故事或案例形式呈現概念
6. 提問引導：使用問題激發思考

請為{chapter_title}中的「{section_title}」小節生成內容，以{difficulty}難度撰寫。"""
        
        user_prompt = f"""請為統計學講義生成「{section_title}」小節的詳細內容，包括：

1. 主要內容 (800-1200字，清晰解釋概念，使用淺顯易懂的語言，並遵循認知負荷理論分解複雜概念)
2. 3個實際應用例子 (與生活或職場相關，使用故事化方式呈現)
3. 2個記憶技巧 (使用縮寫、聯想或視覺化幫助記憶關鍵概念)
4. 3個練習題 (包括問題和答案，由簡單到複雜)

內容必須：
- 科學準確
- 適合大學生理解
- 包含實例和類比
- 使用清晰的段落結構
- 富有趣味性和吸引力"""
        
        try:
            # 調用ai_helper中的generate_explanation函數代替直接調用API
            from ai_helper import generate_explanation
            content = generate_explanation(
                f"為統計學講義生成「{section_title}」小節",
                difficulty
            )
        except Exception as api_error:
            print(f"API調用失敗，使用模擬數據: {str(api_error)}")
            from ai_helper import get_mock_explanation
            content = get_mock_explanation(
                f"統計學講義-{section_title}",
                difficulty
            )
        
        # 構建默認內容
        default_content = {
            "content": f"{section_title}是統計學中的重要概念，它幫助我們理解數據的本質和規律。{section_title}的應用廣泛，從基礎數據分析到複雜的統計推斷都有其重要作用。學習{section_title}需要掌握相關的概念定義、計算方法和實際應用技巧。",
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
                    "answer": f"{section_title}是統計學的重要組成部分，它的核心在於幫助我們從數據中獲取有價值的信息。它的重要性體現在數據分析、決策支持和研究設計等多個方面。"
                },
                {
                    "type": "short_answer",
                    "question": f"描述{section_title}的一個實際應用場景。",
                    "answer": f"在市場研究中，研究人員可以使用{section_title}來分析消費者行為模式，預測市場趨勢，從而幫助企業調整營銷策略。"
                },
                {
                    "type": "short_answer",
                    "question": f"{section_title}與相關統計概念有什麼關係？請詳細說明。",
                    "answer": f"{section_title}與其他統計概念如數據收集、假設檢驗等緊密相連。它們共同構成了完整的統計分析框架，用於解決各種實際問題。理解這些關係有助於更全面地掌握統計學知識體系。"
                }
            ]
        }
        
        # 嘗試解析API返回的內容
        try:
            # 檢查內容是否包含預期的部分
            if "主要內容" in content and "實際應用例子" in content and "記憶技巧" in content and "練習題" in content:
                # 解析主要內容
                content_parts = content.split("實際應用例子")
                main_content = content_parts[0].replace("主要內容", "").strip()
                
                # 解析例子
                examples_parts = content_parts[1].split("記憶技巧")
                examples_text = examples_parts[0].strip()
                examples = [ex.strip() for ex in examples_text.split("\n") if ex.strip() and not ex.startswith("記憶技巧")]
                
                # 處理編號
                clean_examples = []
                for ex in examples:
                    if ex.startswith(("1.", "2.", "3.", "例子1:", "例子2:", "例子3:")):
                        clean_ex = ex.split(":", 1)[1].strip() if ":" in ex else ex[ex.find(".")+1:].strip()
                        clean_examples.append(clean_ex)
                    else:
                        clean_examples.append(ex)
                
                if clean_examples:
                    default_content["examples"] = clean_examples[:3]  # 保證最多3個例子
                
                # 解析記憶技巧
                mnemonics_parts = examples_parts[1].split("練習題")
                mnemonics_text = mnemonics_parts[0].strip()
                mnemonics = [m.strip() for m in mnemonics_text.split("\n") if m.strip() and not m.startswith("練習題")]
                
                # 處理編號
                clean_mnemonics = []
                for m in mnemonics:
                    if m.startswith(("1.", "2.", "技巧1:", "技巧2:")):
                        clean_m = m.split(":", 1)[1].strip() if ":" in m else m[m.find(".")+1:].strip()
                        clean_mnemonics.append(clean_m)
                    else:
                        clean_mnemonics.append(m)
                
                if clean_mnemonics:
                    default_content["mnemonics"] = clean_mnemonics[:2]  # 保證最多2個記憶技巧
                
                # 解析練習題
                exercises_text = mnemonics_parts[1].strip()
                exercise_blocks = exercises_text.split("\n\n")
                
                # 提取問題和答案對
                exercises = []
                for i, block in enumerate(exercise_blocks):
                    if "問題" in block and "答案" in block:
                        parts = block.split("答案")
                        question = parts[0].replace("問題", "").replace(":", "").strip()
                        answer = parts[1].replace(":", "").strip()
                        
                        exercises.append({
                            "type": "short_answer",
                            "question": question,
                            "answer": answer
                        })
                
                if exercises:
                    default_content["exercises"] = exercises[:3]  # 保證最多3個練習題
                
                # 更新主要內容
                if main_content:
                    default_content["content"] = main_content
            
            elif len(content.split("\n\n")) >= 4:
                # 嘗試基於段落分隔解析
                paragraphs = content.split("\n\n")
                default_content["content"] = "\n\n".join(paragraphs[:3])  # 前3段作為主要內容
                
                if len(paragraphs) > 3:
                    # 嘗試提取例子
                    for para in paragraphs[3:]:
                        if "例" in para.lower() or "案例" in para or "應用" in para:
                            examples = para.split("\n")
                            clean_examples = [ex for ex in examples if ex.strip()]
                            if clean_examples:
                                default_content["examples"] = clean_examples[:3]
                            break
        
        except Exception as parse_error:
            print(f"解析內容時出錯: {str(parse_error)}")
            # 使用默認內容，已經初始化
        
        return default_content
    
    except Exception as e:
        print(f"生成內容時發生錯誤: {str(e)}")
        # 返回預設內容
        return {
            "content": f"{section_title}的內容將在此介紹。",
            "examples": [f"{section_title}的應用例子"],
            "mnemonics": [f"{section_title}的記憶技巧"],
            "exercises": [
                {
                    "type": "short_answer",
                    "question": f"請解釋{section_title}的核心概念。",
                    "answer": f"答案包含對{section_title}的詳細解釋。"
                }
            ]
        }

def generate_chapter_content(chapter_number, chapter_title, sections):
    """
    生成完整章節的內容
    
    參數:
        chapter_number (str): 章節編號
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
    
    for i, section_title in enumerate(sections):
        section_number = f"{chapter_number}.{i+1}"
        print(f"正在生成小節 {section_number}: {section_title}...")
        
        section_content = generate_section_content(section_title, chapter_title)
        
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
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已創建講義文件: {filename}")

# 示例使用
if __name__ == "__main__":
    # 第一章：統計學簡介
    chapter1_sections = [
        "統計學的定義與範疇",
        "母體與樣本",
        "資料類型與測量尺度",
        "描述統計與推論統計",
        "統計研究設計流程",
        "資料收集方法",
        "統計學的歷史發展與應用"
    ]
    
    chapter1 = generate_chapter_content(1, "統計學簡介與基本概念", chapter1_sections)
    create_lecture_file(chapter1, os.path.join("講義", "第一章_完整.json"))
    
    # 可以繼續為其他章節生成內容
    # 第二章：資料的摘要與呈現
    chapter2_sections = [
        "資料的組織與呈現",
        "次數分配與長條圖",
        "集中趨勢的測量：平均數、中位數、眾數",
        "變異性的測量：全距、四分位距、標準差",
        "資料的標準化與Z分數",
        "偏態與峰度",
        "圖形化資料呈現方法"
    ]
    
    chapter2 = generate_chapter_content(2, "資料的摘要與呈現", chapter2_sections)
    create_lecture_file(chapter2, os.path.join("講義", "第二章_完整.json")) 