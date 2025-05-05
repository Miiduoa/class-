from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from ai_views import ai_blueprint
from statistics_course_outline import STATISTICS_COURSE_OUTLINE

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 註冊AI功能藍圖
app.register_blueprint(ai_blueprint)

db = SQLAlchemy(app)

# 資料模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    last_visited = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('progress', lazy=True))

# 載入講義資料
def load_course_data():
    course_data = {"chapters": []}
    lecture_dir = os.path.join(os.path.dirname(__file__), '講義')
    
    print(f"正在從 {lecture_dir} 載入講義資料...")
    
    if not os.path.exists(lecture_dir):
        print(f"警告: 講義目錄不存在: {lecture_dir}")
        return course_data
    
    # 先加載所有完整章節文件
    complete_files = [f for f in os.listdir(lecture_dir) if f.endswith('_完整.json') and '章' in f]
    other_files = [f for f in os.listdir(lecture_dir) if f.endswith('.json') and f not in complete_files]
    
    print(f"找到 {len(complete_files)} 個完整章節文件: {complete_files}")
    print(f"找到 {len(other_files)} 個其他JSON文件")
    
    # 先處理完整章節文件
    for filename in sorted(complete_files):
        file_path = os.path.join(lecture_dir, filename)
        print(f"正在處理完整章節文件: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    chapter_data = json.load(f)
                    if "chapters" in chapter_data:
                        print(f"在 {filename} 中找到章節: {len(chapter_data['chapters'])}")
                        for chapter in chapter_data["chapters"]:
                            # 確保每個章節都有必要的屬性
                            if not 'chapterNumber' in chapter:
                                print(f"警告: 在 {filename} 中的章節缺少 chapterNumber")
                                continue
                            if not 'chapterTitle' in chapter:
                                print(f"警告: 章節 {chapter.get('chapterNumber', '未知')} 缺少 chapterTitle")
                                continue
                            if not 'sections' in chapter:
                                print(f"警告: 章節 {chapter.get('chapterNumber', '未知')} 缺少 sections")
                                continue
                            
                            print(f"  - 章節 {chapter.get('chapterNumber', '未知')}: {chapter.get('chapterTitle', '未知')} (包含 {len(chapter.get('sections', []))} 個小節)")
                            
                            # 將章節添加到列表中
                            course_data["chapters"].append(chapter)
                    else:
                        print(f"警告: 在 {filename} 中未找到 'chapters' 鍵")
                except json.JSONDecodeError as e:
                    print(f"錯誤: 載入 {filename} 時發生 JSON 解析錯誤: {e}")
        except Exception as e:
            print(f"錯誤: 無法開啟或讀取檔案 {filename}: {e}")
    
    # 按章節編號排序
    try:
        # 轉換chapterNumber為整數進行排序
        course_data["chapters"] = sorted(course_data["chapters"], 
                                       key=lambda x: int(x["chapterNumber"]) if str(x["chapterNumber"]).isdigit() else x["chapterNumber"])
        print(f"總共載入了 {len(course_data['chapters'])} 個章節，按編號排序完成")
    except Exception as e:
        print(f"錯誤: 排序章節時出錯: {e}")
    
    # 檢查是否有任何章節
    if not course_data["chapters"]:
        print("警告: 未載入任何章節！開始嘗試載入其他文件...")
        
        # 如果沒有從完整章節文件中載入，則嘗試其他文件
        for filename in sorted(other_files):
            file_path = os.path.join(lecture_dir, filename)
            print(f"正在處理文件: {filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        chapter_data = json.load(f)
                        if "chapters" in chapter_data:
                            print(f"在 {filename} 中找到章節: {len(chapter_data['chapters'])}")
                            for chapter in chapter_data["chapters"]:
                                # 確保每個章節都有必要的屬性
                                if not 'chapterNumber' in chapter:
                                    print(f"警告: 在 {filename} 中的章節缺少 chapterNumber")
                                    continue
                                if not 'chapterTitle' in chapter:
                                    print(f"警告: 章節 {chapter.get('chapterNumber', '未知')} 缺少 chapterTitle")
                                    continue
                                if not 'sections' in chapter:
                                    print(f"警告: 章節 {chapter.get('chapterNumber', '未知')} 缺少 sections")
                                    continue
                                
                                print(f"  - 章節 {chapter.get('chapterNumber', '未知')}: {chapter.get('chapterTitle', '未知')} (包含 {len(chapter.get('sections', []))} 個小節)")
                                
                                # 將章節添加到列表中
                                course_data["chapters"].append(chapter)
                        else:
                            print(f"警告: 在 {filename} 中未找到 'chapters' 鍵")
                    except json.JSONDecodeError as e:
                        print(f"錯誤: 載入 {filename} 時發生 JSON 解析錯誤: {e}")
            except Exception as e:
                print(f"錯誤: 無法開啟或讀取檔案 {filename}: {e}")
        
        # 再次排序章節
        try:
            course_data["chapters"] = sorted(course_data["chapters"], 
                                           key=lambda x: int(x["chapterNumber"]) if str(x["chapterNumber"]).isdigit() else x["chapterNumber"])
            print(f"總共載入了 {len(course_data['chapters'])} 個章節，按編號排序完成")
        except Exception as e:
            print(f"錯誤: 排序章節時出錯: {e}")
    
    if not course_data["chapters"]:
        print("錯誤: 嘗試所有文件後仍未載入任何章節！")
    
    return course_data

# 路由
@app.route('/')
def home():
    print("\n===== 載入首頁 =====")
    
    # 直接從統計學完整講義.json載入所有章節內容
    complete_lecture_path = os.path.join(os.path.dirname(__file__), '講義/統計學完整講義.json')
    course_data = {"chapters": []}
    
    if os.path.exists(complete_lecture_path):
        try:
            with open(complete_lecture_path, 'r', encoding='utf-8') as f:
                complete_data = json.load(f)
                if "chapters" in complete_data and complete_data["chapters"]:
                    course_data = complete_data
                    print(f"從完整講義中載入了 {len(course_data['chapters'])} 個章節")
        except Exception as e:
            print(f"讀取完整講義時出錯: {e}")
    
    # 如果未能從完整講義中載入，則使用原方法載入
    if not course_data["chapters"]:
        print("從完整講義載入失敗，嘗試使用原方法載入...")
        course_data = load_course_data()
    
    print(f"載入的章節數量: {len(course_data.get('chapters', []))}")
    
    # 顯示章節標題和詳細內容
    print("\n=== 詳細章節內容 ===")
    for chapter in course_data.get("chapters", []):
        print(f"\n章節 {chapter.get('chapterNumber', '?')}: {chapter.get('chapterTitle', '未知標題')} - {len(chapter.get('sections', []))} 個小節")
        for section in chapter.get('sections', []):
            print(f"  - 小節 {section.get('sectionNumber', '?')}: {section.get('sectionTitle', '未知標題')}")
    
    return render_template('home.html', course_data=course_data)

@app.route('/chapter/<int:chapter_number>')
def chapter(chapter_number):
    course_data = load_course_data()
    
    # 找到當前章節
    current_chapter = None
    for chapter in course_data["chapters"]:
        # 嘗試將chapterNumber轉換為整數進行比較
        try:
            if int(chapter["chapterNumber"]) == chapter_number:
                current_chapter = chapter
                break
        except (ValueError, TypeError):
            # 如果無法轉換，嘗試直接比較字符串
            if str(chapter["chapterNumber"]) == str(chapter_number):
                current_chapter = chapter
                break
    
    if current_chapter is None:
        flash('找不到指定章節!')
        return redirect(url_for('home'))
    
    # 整合講義內容
    lecture_content = load_lecture_content(chapter_number)
    
    # 找尋課程大綱中的對應章節
    outline_chapter = None
    for ch_num, ch_info in STATISTICS_COURSE_OUTLINE.items():
        if int(ch_num) == chapter_number:
            outline_chapter = {
                'chapter': int(ch_num),
                'title': ch_info['title'],
                'sections': ch_info['sections']
            }
            break
    
    # 獲取前一章和後一章
    prev_chapter = None
    next_chapter = None
    for i, ch in enumerate(course_data["chapters"]):
        try:
            if int(ch["chapterNumber"]) == chapter_number:
                if i > 0:
                    prev_chapter = int(course_data["chapters"][i-1]["chapterNumber"])
                if i < len(course_data["chapters"]) - 1:
                    next_chapter = int(course_data["chapters"][i+1]["chapterNumber"])
                break
        except (ValueError, TypeError):
            pass
    
    # 確保current_chapter可以用字典索引訪問
    chapter_dict = {
        'chapter': current_chapter.get('chapterNumber', ''),
        'title': current_chapter.get('chapterTitle', ''),
        'sections': current_chapter.get('sections', []),
        'overview': current_chapter.get('overview', '')
    }
    
    return render_template('chapter.html', 
                           chapter=chapter_dict, 
                           lecture_content=lecture_content,
                           outline_chapter=outline_chapter,
                           prev_chapter=prev_chapter,
                           next_chapter=next_chapter)

@app.route('/section/<int:chapter_number>/<section_number>')
def section(chapter_number, section_number):
    course_data = load_course_data()
    
    # 找到當前章節和小節
    current_section = None
    current_chapter = None
    
    for chapter in course_data["chapters"]:
        # 嘗試將chapterNumber轉換為整數進行比較
        try:
            if int(chapter["chapterNumber"]) == chapter_number:
                current_chapter = chapter
                for section in chapter["sections"]:
                    if section["sectionNumber"] == section_number:
                        current_section = section
                        break
                break
        except (ValueError, TypeError):
            # 如果無法轉換，嘗試直接比較字符串
            if str(chapter["chapterNumber"]) == str(chapter_number):
                current_chapter = chapter
                for section in chapter["sections"]:
                    if section["sectionNumber"] == section_number:
                        current_section = section
                        break
                break
    
    if current_section is None:
        flash('找不到指定小節!')
        return redirect(url_for('chapter', chapter_number=chapter_number))
    
    # 生成適當的圖表或視覺化內容
    plots = generate_plots(chapter_number, section_number)
    
    # 整合講義內容
    section_index = None
    
    # 從課程大綱中找到對應的小節索引
    outline_chapter = None
    for ch_num, ch in STATISTICS_COURSE_OUTLINE.items():
        if int(ch_num) == chapter_number:
            outline_chapter = {
                'chapter': int(ch_num),
                'title': ch['title'],
                'sections': ch['sections']
            }
            for i, sec in enumerate(ch['sections']):
                if sec['title'] == current_section["sectionTitle"]:
                    section_index = i
                    break
            break
    
    # 先從JSON中直接獲取內容
    json_content = None
    if "content" in current_section:
        # Fix the f-string syntax error by using a different approach
        content_text = current_section['content']
        json_content = "<p>" + content_text.replace("\n\n", "</p><p>") + "</p>"
    
    # 然後嘗試從HTML講義中獲取內容
    if section_index is not None:
        # 提取小節相關內容
        section_content = load_section_content(chapter_number, section_index)
        
        # 如果HTML講義中沒有內容，使用JSON中的內容
        if not section_content and json_content:
            section_content = json_content
            
        visualization = extract_visualization(chapter_number, section_index)
        examples = extract_examples(chapter_number, section_index)
        exercises = extract_exercises(chapter_number, section_index)
        
        # 如果沒有從HTML中提取到例子和練習，嘗試從JSON中獲取
        if not examples and "examples" in current_section:
            examples = [f"<p>{example}</p>" for example in current_section["examples"]]
        
        if not exercises and "exercises" in current_section:
            exercises = []
            for exercise in current_section["exercises"]:
                if isinstance(exercise, dict):
                    exercise_html = f"<div class='exercise'><p><strong>問題:</strong> {exercise.get('question', '')}</p>"
                    if "answer" in exercise:
                        exercise_html += f"<p><strong>答案:</strong> {exercise.get('answer', '')}</p></div>"
                    exercises.append(exercise_html)
                else:
                    exercises.append(f"<p>{exercise}</p>")
        
        if outline_chapter:
            learning_objectives = generate_learning_objectives(chapter_number, section_index, current_section["sectionTitle"])
    else:
        # 如果從大綱中找不到對應的小節，直接使用JSON中的內容
        section_content = json_content
        visualization = None
        examples = []
        exercises = []
        
        if "examples" in current_section:
            examples = [f"<p>{example}</p>" for example in current_section["examples"]]
        
        if "exercises" in current_section:
            exercises = []
            for exercise in current_section["exercises"]:
                if isinstance(exercise, dict):
                    exercise_html = f"<div class='exercise'><p><strong>問題:</strong> {exercise.get('question', '')}</p>"
                    if "answer" in exercise:
                        exercise_html += f"<p><strong>答案:</strong> {exercise.get('answer', '')}</p></div>"
                    exercises.append(exercise_html)
                else:
                    exercises.append(f"<p>{exercise}</p>")
        
        learning_objectives = generate_learning_objectives(chapter_number, 0, current_section["sectionTitle"])
    
    # 獲取前一節和後一節
    prev_section = None
    next_section = None
    
    sections = current_chapter.get("sections", [])
    for i, sec in enumerate(sections):
        if sec["sectionNumber"] == section_number:
            if i > 0:
                prev_section = sections[i-1]["sectionNumber"]
            if i < len(sections) - 1:
                next_section = sections[i+1]["sectionNumber"]
            break
    
    # 確保可以用字典索引訪問章節和小節數據
    chapter_dict = {
        'chapter': current_chapter.get('chapterNumber', ''),
        'title': current_chapter.get('chapterTitle', ''),
        'sections': current_chapter.get('sections', []),
        'overview': current_chapter.get('overview', '')
    }
    
    section_dict = {
        'sectionNumber': current_section.get('sectionNumber', ''),
        'sectionTitle': current_section.get('sectionTitle', ''),
        'overview': current_section.get('overview', ''),
        'exercises': current_section.get('exercises', [])
    }
    
    return render_template('section.html', 
                           chapter=chapter_dict, 
                           section=section_dict,
                           plots=plots,
                           section_content=section_content,
                           visualization=visualization,
                           examples=examples,
                           exercises=exercises,
                           learning_objectives=learning_objectives,
                           outline_chapter=outline_chapter,
                           prev_section=prev_section,
                           next_section=next_section)

@app.route('/chapter10')
def chapter10():
    # 讀取第10章所有內容
    chapter_overview = None
    section_10_1 = None
    section_10_2 = None
    section_10_3 = None
    section_10_4 = None
    
    # 讀取概述
    overview_path = os.path.join(os.path.dirname(__file__), '講義/第10章_概述.json')
    if os.path.exists(overview_path):
        with open(overview_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                chapter_overview = chapter.get('overview', '')
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_1 = chapter['sections'][0]
    
    # 讀取 t 檢定內容
    t_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體平均數t檢定.json')
    if os.path.exists(t_test_path):
        with open(t_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_2 = chapter['sections'][0]
    
    # 讀取比例檢定內容
    proportion_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體比例檢定.json')
    if os.path.exists(proportion_test_path):
        with open(proportion_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_3 = chapter['sections'][0]
    
    # 讀取變異數檢定內容
    variance_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體變異數檢定.json')
    if os.path.exists(variance_test_path):
        with open(variance_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_4 = chapter['sections'][0]
    
    # 整合所有內容到一個結構中
    sections = {
        'section_10_1': section_10_1,
        'section_10_2': section_10_2,
        'section_10_3': section_10_3,
        'section_10_4': section_10_4
    }
    
    return render_template('chapter10.html', overview=chapter_overview, sections=sections)

@app.route('/chapter10test')
def chapter10test():
    # 讀取第10章所有內容，與chapter10函數相同
    chapter_overview = None
    section_10_1 = None
    section_10_2 = None
    section_10_3 = None
    section_10_4 = None
    
    # 讀取概述
    overview_path = os.path.join(os.path.dirname(__file__), '講義/第10章_概述.json')
    if os.path.exists(overview_path):
        with open(overview_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                chapter_overview = chapter.get('overview', '')
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_1 = chapter['sections'][0]
    
    # 讀取其他小節內容
    t_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體平均數t檢定.json')
    if os.path.exists(t_test_path):
        with open(t_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_2 = chapter['sections'][0]
    
    proportion_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體比例檢定.json')
    if os.path.exists(proportion_test_path):
        with open(proportion_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_3 = chapter['sections'][0]
    
    variance_test_path = os.path.join(os.path.dirname(__file__), '講義/第10章_母體變異數檢定.json')
    if os.path.exists(variance_test_path):
        with open(variance_test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'chapters' in data and len(data['chapters']) > 0:
                chapter = data['chapters'][0]
                if 'sections' in chapter and len(chapter['sections']) > 0:
                    section_10_4 = chapter['sections'][0]
    
    # 整合內容
    sections = {
        'section_10_1': section_10_1,
        'section_10_2': section_10_2,
        'section_10_3': section_10_3,
        'section_10_4': section_10_4
    }
    
    return render_template('chapter10_test.html', overview=chapter_overview, sections=sections)

def generate_plots(chapter_number, section_number):
    plots = {}
    
    # 依據章節和小節生成適當的圖表
    if chapter_number == 1 and section_number == "1.1":
        # 統計學流程示意圖
        fig, ax = plt.subplots(figsize=(8, 4))
        steps = ['資料收集', '資料整理', '資料分析', '統計推論']
        x = np.arange(len(steps))
        ax.plot(x, [1, 1, 1, 1], 'bo-', linewidth=2, markersize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(steps)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['process_flow'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    if chapter_number == 2 and section_number == "2.5":
        # 準確度與精密度示意圖
        fig, axs = plt.subplots(2, 2, figsize=(8, 8))
        
        # 高準確高精密
        axs[0, 0].set_title('高準確度、高精密度')
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False)
        axs[0, 0].add_patch(circle)
        axs[0, 0].plot([0.5], [0.5], 'ro', markersize=8)
        for _ in range(10):
            x = np.random.normal(0.5, 0.05)
            y = np.random.normal(0.5, 0.05)
            axs[0, 0].plot(x, y, 'bo', markersize=6)
        
        # 低準確高精密
        axs[0, 1].set_title('低準確度、高精密度')
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False)
        axs[0, 1].add_patch(circle)
        axs[0, 1].plot([0.5], [0.5], 'ro', markersize=8)
        for _ in range(10):
            x = np.random.normal(0.7, 0.05)
            y = np.random.normal(0.7, 0.05)
            axs[0, 1].plot(x, y, 'bo', markersize=6)
        
        # 高準確低精密
        axs[1, 0].set_title('高準確度、低精密度')
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False)
        axs[1, 0].add_patch(circle)
        axs[1, 0].plot([0.5], [0.5], 'ro', markersize=8)
        for _ in range(10):
            x = np.random.normal(0.5, 0.15)
            y = np.random.normal(0.5, 0.15)
            axs[1, 0].plot(x, y, 'bo', markersize=6)
        
        # 低準確低精密
        axs[1, 1].set_title('低準確度、低精密度')
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False)
        axs[1, 1].add_patch(circle)
        axs[1, 1].plot([0.5], [0.5], 'ro', markersize=8)
        for _ in range(10):
            x = np.random.normal(0.7, 0.15)
            y = np.random.normal(0.7, 0.15)
            axs[1, 1].plot(x, y, 'bo', markersize=6)
        
        for ax in axs.flat:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['accuracy_precision'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 為第1章生成統計發展史時間線
    if chapter_number == 1 and section_number == "1.2":
        fig, ax = plt.subplots(figsize=(10, 4))
        years = [1662, 1890, 1925, 1950, 1970, 2000]
        events = ['John Graunt\n《自然及政治觀察》', 'Karl Pearson\n協方差與相關係數', 
                 'R.A. Fisher\n最佳線性無偏估計', '電腦運算', '大數據時代', '機器學習']
        
        ax.plot(years, [1]*len(years), 'ko', markersize=12)
        for i, (year, event) in enumerate(zip(years, events)):
            ax.annotate(f'{year}\n{event}', (year, 1), xytext=(0, -30 if i % 2 == 0 else 30), 
                       textcoords='offset points', ha='center', va='center',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3))
        
        ax.set_xlim(min(years)-50, max(years)+50)
        ax.set_ylim(0, 2)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_title('統計學發展時間線')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['timeline'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 為第1章生成參數與統計量的關係圖
    if chapter_number == 1 and section_number == "1.3":
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 母體與樣本的視覺化
        population_circle = plt.Circle((0.3, 0.7), 0.25, fill=True, alpha=0.3, color='blue')
        sample_circle = plt.Circle((0.3, 0.3), 0.15, fill=True, alpha=0.6, color='red')
        
        ax.add_patch(population_circle)
        ax.add_patch(sample_circle)
        
        # 標記母體與樣本
        ax.text(0.3, 0.7, "母體\n(Population)\nN, μ, σ²", ha='center', va='center', fontsize=12)
        ax.text(0.3, 0.3, "樣本\n(Sample)\nn, x̄, s²", ha='center', va='center', fontsize=12)
        
        # 抽樣與推論的箭頭
        ax.annotate("", xy=(0.3, 0.55), xytext=(0.3, 0.45), 
                   arrowprops=dict(arrowstyle="<-", lw=2, color='green'))
        ax.annotate("抽樣", xy=(0.37, 0.5), xytext=(0.37, 0.5), fontsize=12)
        
        ax.annotate("", xy=(0.3, 0.45), xytext=(0.3, 0.55), 
                   arrowprops=dict(arrowstyle="<-", lw=2, color='purple'))
        ax.annotate("推論", xy=(0.23, 0.5), xytext=(0.23, 0.5), fontsize=12)
        
        # 統計研究流程
        steps = ['研究問題定義', '資料收集', '資料分析', '統計推論']
        x_pos = [0.7, 0.7, 0.7, 0.7]
        y_pos = [0.8, 0.6, 0.4, 0.2]
        
        for x, y, step in zip(x_pos, y_pos, steps):
            ax.text(x, y, step, ha='left', va='center', fontsize=12,
                   bbox=dict(boxstyle='round,pad=0.5', fc='lightyellow', ec='orange', alpha=0.8))
            
        for i in range(len(steps)-1):
            ax.annotate("", xy=(x_pos[i+1], y_pos[i+1]), xytext=(x_pos[i], y_pos[i]), 
                       arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('母體與樣本關係與統計推論流程', fontsize=14)
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['parameter_statistic'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 為第3章生成類別資料的圖表示例
    if chapter_number == 3 and section_number == "3.1":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 長條圖
        categories = ['A型', 'B型', 'O型', 'AB型']
        values = [40, 26.7, 20, 13.3]
        
        bars = ax1.bar(categories, values, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        ax1.set_title('血型分布長條圖')
        ax1.set_ylabel('百分比 (%)')
        ax1.set_ylim(0, 50)
        
        # 為長條加上數值標籤
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3點垂直偏移
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # 圓餅圖
        ax2.pie(values, labels=categories, autopct='%1.1f%%',
               colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'],
               explode=(0.05, 0, 0, 0),  # 突出A型
               shadow=True, startangle=90)
        ax2.axis('equal')  # 確保圓餅是圓形
        ax2.set_title('血型分布圓餅圖')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['bar_pie'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 為第3章生成數量資料的圖表示例
    if chapter_number == 3 and section_number == "3.2":
        # 生成一些隨機數據
        np.random.seed(42)
        data = np.random.normal(170, 8, 200)  # 身高數據
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 直方圖
        bins = np.arange(145, 195, 5)
        ax1.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('身高分布直方圖')
        ax1.set_xlabel('身高 (cm)')
        ax1.set_ylabel('頻數')
        
        # 折線圖 (頻率多邊形)
        hist, bin_edges = np.histogram(data, bins=bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        ax2.plot(bin_centers, hist, 'o-', color='red', linewidth=2)
        ax2.set_title('身高分布折線圖')
        ax2.set_xlabel('身高 (cm)')
        ax2.set_ylabel('頻數')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['histogram_line'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 為第3章生成枝葉圖
    if chapter_number == 3 and section_number == "3.3":
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 模擬考試分數數據
        scores = [78, 82, 85, 90, 76, 88, 92, 95, 79, 81, 85, 93, 89, 84, 77]
        
        # 手動繪製枝葉圖
        stems = {}
        for score in sorted(scores):
            stem = score // 10
            leaf = score % 10
            if stem not in stems:
                stems[stem] = []
            stems[stem].append(leaf)
        
        # 按順序繪製枝和葉
        yticks = []
        ylabels = []
        
        for i, (stem, leaves) in enumerate(sorted(stems.items())):
            ax.text(0, i, f"{stem} |", ha='right', va='center', fontsize=12)
            leaf_text = ' '.join(str(leaf) for leaf in sorted(leaves))
            ax.text(0.1, i, leaf_text, ha='left', va='center', fontsize=12)
            yticks.append(i)
            ylabels.append(str(stem))
        
        ax.set_title('考試分數枝葉圖')
        ax.set_xlim(-1, 8)
        ax.set_ylim(-1, len(stems))
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        ax.set_xticks([])
        
        # 添加一條垂直線分隔枝和葉
        ax.axvline(x=0, ymin=0, ymax=len(stems)-1, color='black', linewidth=1.5)
        
        # 添加說明文字
        ax.text(-0.5, -0.5, "枝", ha='center', va='center', fontsize=10)
        ax.text(0.5, -0.5, "葉", ha='center', va='center', fontsize=10)
        ax.text(0.1, len(stems)+0.3, "範例: 7|8 代表 78 分", ha='left', va='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots['stem_leaf'] = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
    # 生成JSON中定義的所有圖片
    # 替換JSON中的路徑為base64編碼的圖片
    if chapter_number == 1:
        if section_number == "1.6":
            # 統計研究設計流程圖
            fig, ax = plt.subplots(figsize=(8, 8))
            
            steps = ['定義研究問題', '設計抽樣方法', '資料收集', '資料整理與編碼', 
                    '資料分析', '結果解釋', '撰寫報告']
            
            y_positions = np.linspace(0.9, 0.1, len(steps))
            
            for i, (step, y) in enumerate(zip(steps, y_positions)):
                ax.add_patch(plt.Rectangle((0.3, y-0.05), 0.4, 0.1, fill=True, 
                                         color=plt.cm.Blues(0.5+i*0.5/len(steps)), 
                                         alpha=0.8))
                ax.text(0.5, y, step, ha='center', va='center', fontsize=12)
                
                if i < len(steps) - 1:
                    ax.annotate("", xy=(0.5, y_positions[i+1]+0.05), xytext=(0.5, y-0.05), 
                               arrowprops=dict(arrowstyle="->", lw=2, color='black'))
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title('統計研究設計流程', fontsize=14)
            ax.axis('off')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['flowchart'] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
    
    if chapter_number == 3:
        if section_number == "3.4":
            # 時間序列數據
            months = ['1月', '2月', '3月', '4月', '5月', '6月', 
                     '7月', '8月', '9月', '10月', '11月', '12月']
            sales = [120, 100, 140, 160, 190, 210, 230, 240, 200, 180, 150, 130]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(months, sales, 'o-', linewidth=2, markersize=8, color='blue')
            
            max_idx = sales.index(max(sales))
            min_idx = sales.index(min(sales))
            
            ax.plot(months[max_idx], sales[max_idx], 'o', markersize=12, color='red')
            ax.annotate(f'最高銷售: {sales[max_idx]}', 
                       (months[max_idx], sales[max_idx]),
                       xytext=(0, 15), textcoords='offset points',
                       ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))
            
            ax.plot(months[min_idx], sales[min_idx], 'o', markersize=12, color='green')
            ax.annotate(f'最低銷售: {sales[min_idx]}', 
                       (months[min_idx], sales[min_idx]),
                       xytext=(0, -15), textcoords='offset points',
                       ha='center', va='top',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))
            
            ax.set_title('全年銷售額時間序列圖', fontsize=14)
            ax.set_ylabel('銷售額 (萬元)', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['time_series'] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
        
        if section_number == "3.5":
            # 兩組數據的箱型圖
            np.random.seed(42)
            group_a = np.random.normal(75, 8, 30)  # 平均75分，標準差8
            group_b = np.random.normal(82, 10, 30)  # 平均82分，標準差10
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # 繪製箱型圖
            boxplot = ax.boxplot([group_a, group_b], patch_artist=True, 
                              labels=['甲組', '乙組'])
            
            # 設置箱型圖顏色
            colors = ['lightblue', 'lightgreen']
            for patch, color in zip(boxplot['boxes'], colors):
                patch.set_facecolor(color)
            
            # 添加數據點
            for i, data in enumerate([group_a, group_b]):
                # 添加數據點並略微抖動x軸位置
                x = np.random.normal(i+1, 0.04, size=len(data))
                ax.plot(x, data, 'o', alpha=0.5, color='gray', markersize=5)
            
            ax.set_title('甲組與乙組考試成績比較', fontsize=14)
            ax.set_ylabel('分數', fontsize=12)
            
            # 添加均值線和標籤
            for i, data in enumerate([group_a, group_b]):
                mean = np.mean(data)
                ax.axhline(y=mean, xmin=(i/2), xmax=((i+1)/2), 
                          color='red', linestyle='dashed', linewidth=2)
                ax.text(i+1, mean+3, f'平均: {mean:.1f}', 
                       ha='center', va='bottom', color='red', fontweight='bold')
            
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['boxplot'] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
        
        if section_number == "3.6":
            # 誤導性圖表示例
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # 使用相同的數據，但展示方式不同
            years = [2018, 2019, 2020, 2021, 2022]
            values = [100, 105, 107, 109, 110]
            
            # 正確的圖表：從0開始的y軸
            ax1.plot(years, values, 'o-', linewidth=2, markersize=8, color='blue')
            ax1.set_title('正確展示：完整比例尺', fontsize=12)
            ax1.set_xlabel('年份', fontsize=10)
            ax1.set_ylabel('數值', fontsize=10)
            ax1.set_ylim(0, max(values) * 1.1)  # 從0開始，留一些上方空間
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # 誤導性的圖表：截斷的y軸
            ax2.plot(years, values, 'o-', linewidth=2, markersize=8, color='red')
            ax2.set_title('誤導性展示：截斷的比例尺', fontsize=12)
            ax2.set_xlabel('年份', fontsize=10)
            ax2.set_ylabel('數值', fontsize=10)
            ax2.set_ylim(95, max(values) * 1.05)  # 從95開始，使增長看起來更明顯
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            # 標示截斷的y軸
            ax2.axhline(y=ax2.get_ylim()[0], color='red', linestyle='-', linewidth=2)
            ax2.text(years[0]-0.5, ax2.get_ylim()[0]+1, '截斷！', color='red', fontweight='bold')
            
            # 添加說明
            fig.suptitle('統計圖表可能的扭曲性示例', fontsize=14)
            plt.figtext(0.5, 0.01, '注意：右圖截斷了y軸，使得相同的數據變化看起來更加顯著', 
                       ha='center', fontsize=10, bbox=dict(boxstyle='round', fc='yellow', alpha=0.5))
            
            plt.tight_layout(rect=[0, 0.05, 1, 0.95])
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['misleading_graph'] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
    
    return plots

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return render_template('search.html', results=None)
    
    course_data = load_course_data()
    results = []
    
    for chapter in course_data["chapters"]:
        for section in chapter["sections"]:
            if (query.lower() in section["sectionTitle"].lower() or 
                query.lower() in section.get("overview", "").lower()):
                results.append({
                    "chapter_number": chapter["chapterNumber"],
                    "chapter_title": chapter["chapterTitle"],
                    "section_number": section["sectionNumber"],
                    "section_title": section["sectionTitle"],
                    "overview": section.get("overview", "")
                })
    
    return render_template('search.html', results=results, query=query)

@app.route('/quiz/<int:chapter_number>/<section_number>')
def quiz(chapter_number, section_number):
    course_data = load_course_data()
    
    # 找到當前章節和小節
    current_section = None
    current_chapter = None
    
    for chapter in course_data["chapters"]:
        if chapter["chapterNumber"] == chapter_number:
            current_chapter = chapter
            for section in chapter["sections"]:
                if section["sectionNumber"] == section_number:
                    current_section = section
                    break
            break
    
    if current_section is None:
        flash('找不到指定小節!')
        return redirect(url_for('chapter', chapter_number=chapter_number))
    
    # 取得小節的測驗題
    exercises = current_section.get("exercises", [])
    
    return render_template('quiz.html', 
                           chapter=current_chapter, 
                           section=current_section,
                           exercises=exercises)

# 新增：統計學講義HTML直接顯示路由
@app.route('/lectures/<lecture_file>')
def show_lecture(lecture_file):
    # 讀取講義HTML文件
    try:
        lecture_path = os.path.join(os.path.dirname(__file__), '網頁講義', lecture_file)
        with open(lecture_path, 'r', encoding='utf-8') as f:
            lecture_content = f.read()
        
        # 提取標題
        title_match = re.search(r'<title>(.*?)</title>', lecture_content, re.IGNORECASE)
        title = "統計學講義" if not title_match else title_match.group(1)
        
        return render_template('layout.html', content=lecture_content, title=title)
    except Exception as e:
        print(f"Error showing lecture: {e}")
        flash(f"無法載入講義: {e}", "danger")
        return redirect(url_for('home'))

@app.route('/lectures')
def lectures_index():
    """顯示所有可用講義的目錄"""
    lectures_dir = os.path.join(os.path.dirname(__file__), '網頁講義')
    
    if not os.path.exists(lectures_dir):
        flash("講義目錄不存在", "warning")
        return redirect(url_for('home'))
    
    lectures = []
    for filename in os.listdir(lectures_dir):
        if filename.endswith('.html'):
            # 嘗試從檔案名稱生成標題
            title = filename.replace('.html', '').replace('_', ' ')
            
            # 從文件內容提取標題 (如果可能)
            try:
                with open(os.path.join(lectures_dir, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1)
            except:
                pass  # 如果無法從文件中提取標題，則使用文件名
            
            lectures.append({"filename": filename, "title": title})
    
    # 按文件名排序，使第N章排在一起
    def get_chapter_num(filename):
        match = re.search(r'第(\d+)章', filename)
        if match:
            return int(match.group(1))
        else:
            return 999  # 非章節文件排在最後
    
    lectures = sorted(lectures, key=lambda x: get_chapter_num(x["filename"]))
    
    return render_template('lectures_index.html', lectures=lectures)

# 講義整合功能
def load_lecture_content(chapter_num):
    """從HTML講義中加載章節內容"""
    try:
        lecture_file = f"網頁講義/第{chapter_num}章_完整.html"
        
        if not os.path.exists(lecture_file):
            return None
            
        with open(lecture_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取正文內容
        body_pattern = re.compile(r'<body>(.*?)</body>', re.DOTALL)
        match = body_pattern.search(content)
        
        if match:
            body_content = match.group(1)
            
            # 清理不需要的元素
            body_content = re.sub(r'<h1>.*?</h1>', '', body_content, count=1)  # 移除標題
            body_content = re.sub(r'<div class="back-to-top">.*?</div>', '', body_content)  # 移除回到頂部按鈕
            
            return body_content
            
        return None
    except Exception as e:
        print(f"加載講義內容錯誤: {str(e)}")
        return None

def load_section_content(chapter_num, section_index):
    """從HTML講義中加載小節內容"""
    try:
        lecture_file = f"網頁講義/第{chapter_num}章_完整.html"
        
        if not os.path.exists(lecture_file):
            return None
            
        with open(lecture_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 獲取章節大綱
        chapter = None
        for ch in STATISTICS_COURSE_OUTLINE:
            if ch['chapter'] == chapter_num:
                chapter = ch
                break
                
        if not chapter or section_index >= len(chapter['sections']):
            return None
            
        section_title = chapter['sections'][section_index]['title']
        
        # 提取小節內容
        section_pattern = re.compile(r'<h2>(.*?)</h2>.*?(?=<h2>|<div class="back-to-top">|$)', re.DOTALL)
        matches = section_pattern.findall(content)
        
        if not matches or len(matches) <= section_index:
            return None
            
        # 查找匹配的小節
        section_content = None
        for match in matches:
            if section_title in match:
                # 找到匹配的小節標題
                section_index = matches.index(match)
                section_pattern = re.compile(r'<h2>.*?</h2>(.*?)(?=<h2>|<div class="back-to-top">|$)', re.DOTALL)
                section_matches = section_pattern.findall(content)
                if section_matches and len(section_matches) > section_index:
                    section_content = section_matches[section_index]
                break
                
        if not section_content:
            # 按順序取對應的小節
            section_pattern = re.compile(r'<h2>.*?</h2>(.*?)(?=<h2>|<div class="back-to-top">|$)', re.DOTALL)
            section_matches = section_pattern.findall(content)
            if section_matches and len(section_matches) > section_index:
                section_content = section_matches[section_index]
                
        return section_content
    except Exception as e:
        print(f"加載小節內容錯誤: {str(e)}")
        return None

def extract_visualization(chapter_num, section_index):
    """從HTML講義中提取視覺化內容"""
    try:
        section_content = load_section_content(chapter_num, section_index)
        
        if not section_content:
            return None
            
        # 提取圖片
        img_pattern = re.compile(r'<img.*?src="(.*?)".*?>', re.DOTALL)
        matches = img_pattern.findall(section_content)
        
        if matches:
            return matches[0]  # 返回第一個圖片
            
        return None
    except Exception as e:
        print(f"提取視覺化內容錯誤: {str(e)}")
        return None

def extract_examples(chapter_num, section_index):
    """從HTML講義中提取例子內容"""
    try:
        section_content = load_section_content(chapter_num, section_index)
        
        if not section_content:
            return []
            
        # 提取例子
        example_pattern = re.compile(r'<div class="example">(.*?)</div>', re.DOTALL)
        matches = example_pattern.findall(section_content)
        
        return matches
    except Exception as e:
        print(f"提取例子內容錯誤: {str(e)}")
        return []

def extract_exercises(chapter_num, section_index):
    """從HTML講義中提取練習內容"""
    try:
        section_content = load_section_content(chapter_num, section_index)
        
        if not section_content:
            return []
            
        # 提取練習
        exercise_pattern = re.compile(r'<div class="exercise">(.*?)</div>', re.DOTALL)
        matches = exercise_pattern.findall(section_content)
        
        return matches
    except Exception as e:
        print(f"提取練習內容錯誤: {str(e)}")
        return []

def generate_learning_objectives(chapter_num, section_index, section_title):
    """根據章節和小節生成學習目標"""
    objectives = []
    
    # 根據章節和小節定義學習目標
    if chapter_num == 1:
        if section_index == 0:  # 統計學的定義與範疇
            objectives = [
                "理解統計學的基本定義和應用範圍",
                "區分描述統計和推論統計的不同作用",
                "認識統計學在各領域中的重要性"
            ]
        elif section_index == 1:  # 母體與樣本
            objectives = [
                "理解母體和樣本的概念及其關係",
                "認識抽樣的重要性及其在統計分析中的角色",
                "學習如何從母體中正確抽取具代表性的樣本"
            ]
        elif section_index == 2:  # 測量尺度
            objectives = [
                "區分名目、順序、區間和比率四種測量尺度",
                "理解各種測量尺度的特性和適用範圍",
                "學習如何為不同類型的數據選擇適當的測量尺度"
            ]
    elif chapter_num == 2:
        if section_index == 0:  # 抽樣方法
            objectives = [
                "理解各種抽樣方法的原理和特點",
                "學習如何選擇適合研究目的的抽樣方法",
                "認識抽樣誤差及減少誤差的方法"
            ]
        # 可以繼續添加更多章節的學習目標
    
    # 如果沒有預定義的目標，生成通用目標
    if not objectives:
        objectives = [
            f"理解{section_title}的核心概念和基本原理",
            f"掌握{section_title}的應用方法和計算技巧",
            f"學習如何在實際問題中運用{section_title}相關知識"
        ]
    
    return objectives

# 整合課程路由
@app.route('/course')
def course_index():
    try:
        # 加載課程大綱
        course_data = []
        for chapter_num, chapter_info in STATISTICS_COURSE_OUTLINE.items():
            chapter_data = {
                'chapter': int(chapter_num),
                'title': chapter_info['title'],
                'sections': chapter_info['sections']
            }
            course_data.append(chapter_data)
        
        # 按章節編號排序
        course_data.sort(key=lambda x: x['chapter'])
        
        return render_template('course_index.html', course_data=course_data)
    except Exception as e:
        flash(f'加載課程資料失敗: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/course/chapter/<int:chapter_num>')
def course_chapter(chapter_num):
    try:
        # 加載課程大綱
        course_data = []
        chapter_dict = {}
        for ch_num, ch_info in STATISTICS_COURSE_OUTLINE.items():
            ch_data = {
                'chapter': int(ch_num),
                'title': ch_info['title'],
                'sections': ch_info['sections']
            }
            course_data.append(ch_data)
            if int(ch_num) == chapter_num:
                chapter_dict = ch_data
        
        # 按章節編號排序
        course_data.sort(key=lambda x: x['chapter'])
        
        # 找到對應章節
        chapter = None
        for ch in course_data:
            if ch['chapter'] == chapter_num:
                chapter = ch
                break
        
        if not chapter:
            flash(f'找不到第{chapter_num}章', 'warning')
            return redirect(url_for('course_index'))
        
        # 獲取前一章和後一章
        prev_chapter = None
        next_chapter = None
        
        for i, ch in enumerate(course_data):
            if ch['chapter'] == chapter_num:
                if i > 0:
                    prev_chapter = course_data[i-1]['chapter']
                if i < len(course_data) - 1:
                    next_chapter = course_data[i+1]['chapter']
                break
        
        # 加載章節內容
        chapter_content = load_lecture_content(chapter_num)
        
        return render_template('course_chapter.html', 
                              chapter=chapter, 
                              chapter_content=chapter_content,
                              prev_chapter=prev_chapter,
                              next_chapter=next_chapter)
    except Exception as e:
        flash(f'加載章節資料失敗: {str(e)}', 'danger')
        return redirect(url_for('course_index'))

@app.route('/course/chapter/<int:chapter_num>/section/<int:section_index>')
def course_section(chapter_num, section_index):
    try:
        # 加載課程大綱
        course_data = {}
        for ch_num, ch_info in STATISTICS_COURSE_OUTLINE.items():
            course_data[int(ch_num)] = ch_info
        
        # 找到對應章節
        if chapter_num not in course_data:
            flash(f'找不到第{chapter_num}章', 'warning')
            return redirect(url_for('course_index'))
        
        chapter = {
            'chapter': chapter_num,
            'title': course_data[chapter_num]['title'],
            'sections': course_data[chapter_num]['sections']
        }
        
        # 找到對應小節
        if section_index < 0 or section_index >= len(chapter['sections']):
            flash(f'找不到第{chapter_num}.{section_index+1}節', 'warning')
            return redirect(url_for('course_chapter', chapter_num=chapter_num))
            
        section = chapter['sections'][section_index]
        
        # 獲取前一節和後一節
        prev_section = None
        next_section = None
        
        if section_index > 0:
            prev_section = {
                'chapter_number': chapter_num,
                'section_index': section_index - 1
            }
        elif chapter_num > 1:
            # 前一章的最後一節
            prev_chapter_num = chapter_num - 1
            if prev_chapter_num in course_data:
                prev_section = {
                    'chapter_number': prev_chapter_num,
                    'section_index': len(course_data[prev_chapter_num]['sections']) - 1
                }
        
        if section_index < len(chapter['sections']) - 1:
            next_section = {
                'chapter_number': chapter_num,
                'section_index': section_index + 1
            }
        elif chapter_num < max(course_data.keys()):
            # 下一章的第一節
            next_chapter_num = chapter_num + 1
            if next_chapter_num in course_data:
                next_section = {
                    'chapter_number': next_chapter_num,
                    'section_index': 0
                }
        
        # 加載小節內容
        section_content = load_section_content(chapter_num, section_index)
        visualization = extract_visualization(chapter_num, section_index)
        examples = extract_examples(chapter_num, section_index)
        exercises = extract_exercises(chapter_num, section_index)
        
        # 生成學習目標
        learning_objectives = generate_learning_objectives(chapter_num, section_index, section['title'])
        
        return render_template('course_section.html', 
                              chapter=chapter,
                              section=section,
                              section_index=section_index,
                              section_content=section_content,
                              visualization=visualization,
                              examples=examples,
                              exercises=exercises,
                              learning_objectives=learning_objectives,
                              prev_section=prev_section,
                              next_section=next_section)
    except Exception as e:
        flash(f'加載小節資料失敗: {str(e)}', 'danger')
        return redirect(url_for('course_chapter', chapter_num=chapter_num))

@app.route('/complete_course')
def complete_course():
    """直接從統計學完整講義.json載入所有章節內容"""
    complete_lecture_path = os.path.join(os.path.dirname(__file__), '講義/統計學完整講義.json')
    
    if not os.path.exists(complete_lecture_path):
        flash('完整講義檔案不存在!')
        return redirect(url_for('home'))
    
    try:
        with open(complete_lecture_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
            
        # 確保chapters數據正確
        if not "chapters" in course_data or not course_data["chapters"]:
            flash('完整講義檔案中未找到章節資料!')
            return redirect(url_for('home'))
            
        print(f"從完整講義中載入了 {len(course_data['chapters'])} 個章節")
        
        # 顯示章節詳細資訊
        for chapter in course_data["chapters"]:
            print(f"章節 {chapter.get('chapterNumber', '?')}: {chapter.get('chapterTitle', '未知標題')} - {len(chapter.get('sections', []))} 個小節")
            
        return render_template('home.html', course_data=course_data)
    except Exception as e:
        flash(f'載入完整講義時發生錯誤: {str(e)}')
        return redirect(url_for('home'))

@app.route('/complete_chapter/<int:chapter_number>')
def complete_chapter(chapter_number):
    """直接從對應章節的完整JSON文件載入章節內容"""
    chapter_file_path = os.path.join(os.path.dirname(__file__), f'講義/第{chapter_number}章_完整.json')
    
    if not os.path.exists(chapter_file_path):
        flash(f'第{chapter_number}章完整講義檔案不存在!')
        return redirect(url_for('chapter', chapter_number=chapter_number))
    
    try:
        with open(chapter_file_path, 'r', encoding='utf-8') as f:
            chapter_data = json.load(f)
            
        # 確保chapters數據正確
        if not "chapters" in chapter_data or not chapter_data["chapters"]:
            flash(f'第{chapter_number}章完整講義檔案中未找到章節資料!')
            return redirect(url_for('chapter', chapter_number=chapter_number))
            
        current_chapter = None
        for chapter in chapter_data["chapters"]:
            if str(chapter.get('chapterNumber', '')) == str(chapter_number):
                current_chapter = chapter
                break
                
        if not current_chapter:
            flash(f'在完整講義檔案中未找到第{chapter_number}章!')
            return redirect(url_for('chapter', chapter_number=chapter_number))
            
        print(f"從完整講義中載入了第{chapter_number}章，包含 {len(current_chapter.get('sections', []))} 個小節")
        
        # 找尋課程大綱中的對應章節
        outline_chapter = None
        for ch_num, ch_info in STATISTICS_COURSE_OUTLINE.items():
            if int(ch_num) == chapter_number:
                outline_chapter = {
                    'chapter': int(ch_num),
                    'title': ch_info['title'],
                    'sections': ch_info['sections']
                }
                break
        
        # 封裝章節數據
        chapter_dict = {
            'chapter': current_chapter.get('chapterNumber', ''),
            'title': current_chapter.get('chapterTitle', ''),
            'sections': current_chapter.get('sections', []),
            'overview': current_chapter.get('overview', '')
        }
        
        return render_template('chapter.html', 
                               chapter=chapter_dict, 
                               lecture_content=None,
                               outline_chapter=outline_chapter,
                               prev_chapter=chapter_number-1 if chapter_number > 1 else None,
                               next_chapter=chapter_number+1 if chapter_number < 16 else None)
    except Exception as e:
        flash(f'載入第{chapter_number}章完整講義時發生錯誤: {str(e)}')
        return redirect(url_for('chapter', chapter_number=chapter_number))

@app.route('/display_all_chapters')
def display_all_chapters():
    """顯示所有章節的內容"""
    try:
        # 收集所有章節的數據
        all_chapters = []
        
        # 加載統計學完整講義檔案
        complete_lecture_path = os.path.join(os.path.dirname(__file__), '講義/統計學完整講義.json')
        if os.path.exists(complete_lecture_path):
            with open(complete_lecture_path, 'r', encoding='utf-8') as f:
                complete_data = json.load(f)
                if "chapters" in complete_data:
                    all_chapters = complete_data["chapters"]
                    print(f"從完整講義中載入了 {len(all_chapters)} 個章節")
        
        # 如果沒有從完整講義中加載，則嘗試逐一加載各章節
        if not all_chapters:
            for chapter_num in range(1, 17):  # 16個章節
                chapter_path = os.path.join(os.path.dirname(__file__), f'講義/第{chapter_num}章_完整.json')
                if os.path.exists(chapter_path):
                    with open(chapter_path, 'r', encoding='utf-8') as f:
                        chapter_data = json.load(f)
                        if "chapters" in chapter_data and chapter_data["chapters"]:
                            for chapter in chapter_data["chapters"]:
                                if str(chapter.get('chapterNumber', '')) == str(chapter_num):
                                    all_chapters.append(chapter)
                                    print(f"已加載第{chapter_num}章")
                                    break
        
        # 按章節編號排序
        all_chapters = sorted(all_chapters, key=lambda x: int(x["chapterNumber"]) if str(x["chapterNumber"]).isdigit() else x["chapterNumber"])
        
        return render_template('all_chapters.html', chapters=all_chapters)
    except Exception as e:
        flash(f'載入所有章節時發生錯誤: {str(e)}')
        return redirect(url_for('home'))

@app.route('/statistics_content')
def statistics_content():
    """顯示統計學內容一覽頁面，整合章節和講義資料"""
    # 從統計學大綱載入章節資料
    chapters = []
    for ch_num, ch_info in STATISTICS_COURSE_OUTLINE.items():
        chapters.append({
            'chapter': int(ch_num),
            'title': ch_info['title'],
            'sections': ch_info['sections']
        })
    
    # 依章節編號排序
    chapters = sorted(chapters, key=lambda x: x['chapter'])
    
    # 獲取講義文件列表
    lectures_dir = os.path.join(os.path.dirname(__file__), '網頁講義')
    lectures = []
    
    if os.path.exists(lectures_dir):
        for filename in os.listdir(lectures_dir):
            if filename.endswith('.html'):
                title = filename.replace('.html', '').replace('_', ' ')
                lectures.append({"filename": filename, "title": title})
    
    return render_template('statistics_content.html', chapters=chapters, lectures=lectures)

# 初始化資料庫
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5003) 