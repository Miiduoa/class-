from flask import Blueprint, render_template, request, jsonify, current_app
import ai_helper as ai

ai_blueprint = Blueprint('ai', __name__, url_prefix='/ai')

@ai_blueprint.route('/explain', methods=['GET', 'POST'])
def explain_concept():
    """提供概念解釋功能的路由"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        difficulty = request.form.get('difficulty', 'intermediate')
        
        if not topic:
            return jsonify({"error": "缺少主題參數"}), 400
        
        explanation = ai.generate_explanation(topic, difficulty)
        return jsonify({"explanation": explanation})
    
    return render_template('ai/explain.html')

@ai_blueprint.route('/practice', methods=['GET', 'POST'])
def generate_practice():
    """提供練習題生成功能的路由"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        number = request.form.get('number', 3, type=int)
        difficulty = request.form.get('difficulty', 'intermediate')
        
        if not topic:
            return jsonify({"error": "缺少主題參數"}), 400
        
        questions = ai.generate_practice_questions(topic, number, difficulty)
        return jsonify({"questions": questions})
    
    return render_template('ai/practice.html')

@ai_blueprint.route('/study-plan', methods=['GET', 'POST'])
def create_study_plan():
    """提供學習計劃生成功能的路由"""
    if request.method == 'POST':
        topics = request.form.getlist('topics')
        duration_weeks = request.form.get('duration_weeks', 4, type=int)
        
        if not topics:
            return jsonify({"error": "缺少主題參數"}), 400
        
        plan = ai.generate_study_plan(topics, duration_weeks)
        return jsonify({"plan": plan})
    
    return render_template('ai/study_plan.html')

@ai_blueprint.route('/chat-assistant', methods=['GET', 'POST'])
def chat_assistant():
    """提供AI聊天助手功能的路由"""
    if request.method == 'POST':
        message = request.json.get('message')
        history = request.json.get('history', [])
        
        if not message:
            return jsonify({"error": "缺少訊息內容"}), 400
        
        response = ai.generate_chat_response(message, history)
        return jsonify({"response": response})
    
    return render_template('ai/chat_assistant.html')

@ai_blueprint.route('/chat', methods=['POST'])
def chat():
    """提供聊天API的路由，處理聊天助手的AJAX請求"""
    message = request.json.get('message')
    history = request.json.get('history', [])
    
    if not message:
        return jsonify({"error": "缺少訊息內容"}), 400
    
    try:
        response = ai.generate_chat_response(message, history)
        return jsonify({"response": response})
    except Exception as e:
        current_app.logger.error(f"聊天生成錯誤: {str(e)}")
        return jsonify({"error": "處理請求時發生錯誤", "response": "很抱歉，處理您的請求時發生錯誤。請稍後再試。"}), 500 