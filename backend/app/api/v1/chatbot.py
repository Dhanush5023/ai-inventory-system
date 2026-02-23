from flask import Blueprint, request, jsonify
from ...models.database import get_db
from ...schemas.chatbot import ChatRequest, ChatResponse
from ...ai.chatbot.assistant import assistant
from ...core.security import login_required, get_current_user_id, roles_required

bp = Blueprint("chatbot", __name__)

@bp.route("/query", methods=["POST"])
@login_required
@roles_required("admin", "manager")
def query_assistant():
    """
    Ask a business question to the AI Smart Decision Assistant
    """
    db = get_db()
    try:
        chat_request = ChatRequest(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    try:
        # Call synchronous answer_question
        answer = assistant.answer_question(chat_request.question, db)
        return jsonify(ChatResponse(answer=answer).model_dump())
    except Exception as e:
        return jsonify({"detail": f"AI Assistant Error: {str(e)}"}), 500
