from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...models.database import get_db
from ...schemas.chatbot import ChatRequest, ChatResponse
from ...ai.chatbot.assistant import assistant
from ...core.security import get_current_user_id

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def query_assistant(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Ask a business question to the AI Smart Decision Assistant
    """
    try:
        answer = await assistant.answer_question(request.question, db)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Assistant Error: {str(e)}"
        )
