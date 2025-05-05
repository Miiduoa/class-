from flask import Blueprint, render_template, request, jsonify, current_app
from ai_helper import (
    generate_explanation, 
    generate_practice_questions, 
    generate_study_plan,
    get_api_status, 
    update_api_config,
    test_api_connection,
    chat_with_assistant
)
import logging
from statistics_course_outline import STATISTICS_COURSE_OUTLINE

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/explain')
def explain_concept():
    return render_template('ai/explain_concept.html')

@ai_bp.route('/explain/process', methods=['POST'])
def process_explanation():
    try:
        print(f"接收到概念解釋請求，請求方式: {request.method}")
        
        topic = request.form.get('topic')
        difficulty = request.form.get('difficulty', 'intermediate')
        
        print(f"請求參數: 主題={topic}, 難度={difficulty}")
        
        if not topic:
            error_msg = '請提供要解釋的主題'
            print(f"錯誤: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
        
        try:
            print(f"開始生成解釋: 主題={topic}, 難度={difficulty}")
            answer = generate_explanation(topic, difficulty)
            print(f"解釋生成完成，內容長度: {len(answer) if answer else 0}")
            
            return jsonify({
                'success': True,
                'explanation': answer
            })
        except Exception as e:
            error_msg = f"生成解釋時出錯: {str(e)}"
            logging.error(error_msg)
            print(f"生成過程異常: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
    except Exception as req_e:
        error_msg = f"處理解釋請求時出錯: {str(req_e)}"
        logging.error(error_msg)
        print(f"請求處理異常: {error_msg}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': error_msg
        })

@ai_bp.route('/practice')
def generate_practice():
    return render_template('ai/generate_practice.html')

@ai_bp.route('/practice/generate', methods=['POST'])
def generate_practice_route():
    try:
        print(f"接收到練習題請求，請求方式: {request.method}")
        
        # 初始化默認值
        topic = None
        num_questions = 3
        difficulty = 'intermediate'
        
        # 檢查是否為表單數據
        if request.content_type and 'multipart/form-data' in request.content_type:
            print("檢測到表單數據")
            topic = request.form.get('topic')
            if request.form.get('number'):
                try:
                    num_questions = int(request.form.get('number'))
                except ValueError:
                    num_questions = 3
            difficulty = request.form.get('difficulty', 'intermediate')
            print(f"從表單獲取的參數: 主題={topic}, 數量={num_questions}, 難度={difficulty}")
        
        # 檢查是否為JSON數據
        elif request.content_type and 'application/json' in request.content_type:
            print("檢測到JSON數據")
            json_data = request.get_json(silent=True)
            if json_data:
                topic = json_data.get('topic')
                if json_data.get('number'):
                    try:
                        num_questions = int(json_data.get('number'))
                    except ValueError:
                        num_questions = 3
                difficulty = json_data.get('difficulty', 'intermediate')
                print(f"從JSON獲取的參數: 主題={topic}, 數量={num_questions}, 難度={difficulty}")
        
        # 嘗試從請求參數中獲取數據
        else:
            print("檢測到普通表單數據")
            topic = request.form.get('topic')
            if request.form.get('number'):
                try:
                    num_questions = int(request.form.get('number'))
                except ValueError:
                    num_questions = 3
            difficulty = request.form.get('difficulty', 'intermediate')
            print(f"從表單獲取的參數: 主題={topic}, 數量={num_questions}, 難度={difficulty}")
        
        # 驗證參數
        if not topic:
            error_msg = '請提供問題主題'
            print(f"錯誤: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
        
        try:
            print(f"開始調用生成函數: 主題={topic}, 數量={num_questions}, 難度={difficulty}")
            questions = generate_practice_questions(topic, num_questions, difficulty)
            print(f"生成函數返回，內容長度: {len(questions) if questions else 0}")
            
            if not questions:
                print("警告: 生成結果為空")
            
            return jsonify({
                'success': True,
                'questions': questions
            })
        except Exception as e:
            error_msg = f"生成練習題時出錯: {str(e)}"
            logging.error(error_msg)
            print(f"生成過程異常: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
    except Exception as req_e:
        error_msg = f"處理練習題請求時出錯: {str(req_e)}"
        logging.error(error_msg)
        print(f"請求處理異常: {error_msg}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': error_msg
        })

@ai_bp.route('/study-plan')
def create_study_plan():
    return render_template('ai/create_study_plan.html', STATISTICS_COURSE_OUTLINE=STATISTICS_COURSE_OUTLINE)

@ai_bp.route('/study-plan/generate', methods=['POST'])
def generate_study_plan_route():
    topics = request.form.getlist('topics')
    duration_weeks = request.form.get('duration_weeks', '4')
    goal = request.form.get('goal')
    current_level = request.form.get('current_level', 'intermediate')
    weekly_hours = request.form.get('weekly_hours', '5')
    include_resources = request.form.get('include_resources') == 'true'
    
    print(f"接收到學習計劃生成請求: 主題={topics}, 時長={duration_weeks}週, 目標={goal}, 級別={current_level}, 每週時間={weekly_hours}小時, 包含資源={include_resources}")
    
    if not topics:
        return jsonify({
            'success': False,
            'error': '請選擇至少一個主題'
        })
    
    try:
        duration_weeks = int(duration_weeks)
    except ValueError:
        duration_weeks = 4
    
    try:
        weekly_hours = int(weekly_hours)
    except ValueError:
        weekly_hours = 5
    
    # 將主題編號轉換為主題名稱
    topic_names = []
    for topic_id in topics:
        if topic_id in STATISTICS_COURSE_OUTLINE:
            topic_names.append(STATISTICS_COURSE_OUTLINE[topic_id]['title'])
    
    try:
        plan = generate_study_plan(
            topic_names, 
            duration_weeks, 
            goal, 
            current_level, 
            weekly_hours, 
            include_resources
        )
        return jsonify({
            'success': True,
            'plan': plan
        })
    except Exception as e:
        logging.error(f"生成學習計劃時出錯: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'生成學習計劃時出錯: {str(e)}'
        })

@ai_bp.route('/chat')
def chat_assistant():
    return render_template('ai/chat_assistant.html')

@ai_bp.route('/chat/send', methods=['POST'])
def chat_send_route():
    """處理聊天消息發送請求"""
    print(f"[chat_send_route] Received request: Method={request.method}")
    
    try:
        # 檢查數據類型
        if not request.is_json:
            print("[chat_send_route] Error: Request is not JSON")
            return jsonify({
                "success": False,
                "error": "請求格式不正確，需要JSON格式"
            }), 415
        
        # 獲取數據
        data = request.get_json()
        print(f"[chat_send_route] Received JSON data: {data}")
        
        # 檢查必要參數
        if 'message' not in data:
            print("[chat_send_route] Error: Missing 'message' parameter")
            return jsonify({
                "success": False,
                "error": "缺少必要參數: message"
            }), 400
        
        message = data.get('message', '')
        history = data.get('history', [])
        
        print(f"[chat_send_route] Processing message: '{message}' with history length: {len(history)}")
        
        # 調用AI助手生成回應
        result = chat_with_assistant(message, history)
        
        print(f"[chat_send_route] Got result: success={result.get('success', False)}")
        
        if result.get('success', False):
            return jsonify({
                "success": True,
                "answer": result.get('answer', "處理請求時發生錯誤")
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', "處理請求時發生錯誤"),
                "details": result.get('details', "無詳細信息")
            })
    
    except Exception as e:
        print(f"[chat_send_route] Exception occurred: {str(e)}")
        return jsonify({
            "success": False,
            "error": "處理請求時發生錯誤",
            "details": str(e)
        }), 500

@ai_bp.route('/api/status', methods=['GET'])
def get_api_status_route():
    status = get_api_status()
    return jsonify({
        'success': True,
        'status': status
    })

@ai_bp.route('/api/config', methods=['POST'])
def update_api_config_route():
    api_key = request.form.get('api_key')
    api_base = request.form.get('api_base')
    
    success, message = update_api_config(api_key, api_base)
    return jsonify({
        'success': success,
        'message': message
    })

@ai_bp.route('/api/test', methods=['POST'])
def test_api_connection_route():
    success, message = test_api_connection()
    return jsonify({
        'success': success,
        'message': message
    }) 