import os
import json
import argparse
from statistics_course_outline import STATISTICS_COURSE_OUTLINE
from generate_with_chatgpt import generate_specific_chapter

"""
統計學講義生成腳本

使用ChatGPT生成統計學課程的所有章節講義內容。
根據提供的課程大綱，生成包含心理學學習原則的內容。
"""

def generate_all_chapters():
    """生成所有章節的講義內容"""
    print("===== 開始生成統計學全部章節講義 =====")
    
    # 確保存在講義目錄
    lecture_dir = "講義"
    if not os.path.exists(lecture_dir):
        os.makedirs(lecture_dir)
    
    # 遍歷課程大綱，生成每一章
    for chapter_num, chapter_data in STATISTICS_COURSE_OUTLINE.items():
        chapter_title = chapter_data["title"]
        sections = [section["title"] for section in chapter_data["sections"]]
        
        generate_specific_chapter(int(chapter_num), chapter_title, sections)
    
    print("===== 完成全部章節生成 =====")

def create_combined_file():
    """合併所有章節文件為一個完整的講義文件"""
    print("\n===== 開始合併為完整講義文件 =====")
    
    lecture_dir = "講義"
    combined_data = {
        "courseTitle": "大學統計學",
        "version": "1.0",
        "chapters": []
    }
    
    # 遍歷所有章節文件並合併
    for chapter_num in sorted([int(k) for k in STATISTICS_COURSE_OUTLINE.keys()]):
        file_path = os.path.join(lecture_dir, f"第{chapter_num}章_完整.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 從單個章節文件中提取章節數據
                if "chapters" in data and len(data["chapters"]) > 0:
                    combined_data["chapters"].append(data["chapters"][0])
    
    # 保存合併後的文件
    output_path = os.path.join(lecture_dir, "統計學完整講義.json")
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2)
    
    print(f"完整講義文件已保存至: {output_path}")
    print("===== 完成合併 =====")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成統計學講義內容")
    parser.add_argument("--all", action="store_true", help="生成所有章節的講義")
    parser.add_argument("--chapter", type=int, help="生成特定章節的講義")
    parser.add_argument("--combine", action="store_true", help="合併所有章節為完整講義文件")
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_chapters()
    elif args.chapter is not None:
        chapter_num = args.chapter
        if str(chapter_num) in STATISTICS_COURSE_OUTLINE:
            chapter_data = STATISTICS_COURSE_OUTLINE[str(chapter_num)]
            chapter_title = chapter_data["title"]
            sections = [section["title"] for section in chapter_data["sections"]]
            generate_specific_chapter(chapter_num, chapter_title, sections)
        else:
            print(f"錯誤：找不到第{chapter_num}章")
    elif args.combine:
        create_combined_file()
    else:
        parser.print_help() 