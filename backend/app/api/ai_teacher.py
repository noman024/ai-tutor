from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.app.services.ai_cache import get_cached_answer, set_cached_answer
from backend.app.core.config import get_settings
from fastapi.security import OAuth2PasswordBearer
from backend.app.api.auth import get_current_user
from backend.app.models.user import User
import openai
import google.generativeai as genai
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger("ai_teacher")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
def ask_ai(
    data: AskRequest,
    current_user: User = Depends(get_current_user)
):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    # Check cache
    cached = get_cached_answer(question)
    if cached:
        return {"answer": cached, "cached": True, "provider": "cache"}
    # Try OpenAI first
    try:
        openai.api_key = settings.OPENAI_API_KEY.get_secret_value()
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[{"role": "user", "content": question}],
            temperature=0.7,
            max_tokens=512
        )
        answer = response.choices[0].message.content.strip()
        set_cached_answer(question, answer)
        return {"answer": answer, "cached": False, "provider": "openai"}
    except Exception as e:
        logger.warning(f"OpenAI failed: {e}")
    # Fallback to Gemini
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
        model = genai.GenerativeModel("gemini-1.5-pro")
        gemini_response = model.generate_content(question)
        answer = gemini_response.text.strip()
        set_cached_answer(question, answer)
        return {"answer": answer, "cached": False, "provider": "gemini"}
    except Exception as e:
        logger.error(f"Gemini failed: {e}")
        raise HTTPException(status_code=500, detail="AI models are currently unavailable.") 