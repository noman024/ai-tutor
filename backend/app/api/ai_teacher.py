from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.app.services.ai_cache import get_cached_answer, set_cached_answer
from backend.app.core.config import get_settings
from fastapi.security import OAuth2PasswordBearer
from backend.app.api.auth import get_current_user
from backend.app.models.user import User
from openai import OpenAI
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
    logger.info(f"Received question from user {current_user.email}: {question}")
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    # Check cache
    cached = get_cached_answer(question)
    if cached:
        logger.info(f"Cache hit for question: {question}")
        return {"answer": cached, "cached": True, "provider": "cache"}
    
    logger.info("Cache miss, trying OpenAI...")
    # Try OpenAI first
    try:
        api_key = settings.OPENAI_API_KEY.get_secret_value()
        logger.info(f"OpenAI API key configured (first 8 chars: {api_key[:8]}...)")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Log the exact request we're about to make
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7,
            "max_tokens": 512
        }
        logger.info(f"Making OpenAI request with data: {request_data}")
        
        # Make the request using the new client
        response = client.chat.completions.create(**request_data)
        
        # Log the raw response
        logger.info(f"OpenAI raw response: {response}")
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"OpenAI request successful. Answer length: {len(answer)}")
        set_cached_answer(question, answer)
        return {"answer": answer, "cached": False, "provider": "openai"}
    except Exception as e:
        logger.error(f"OpenAI request failed with error: {str(e)}", exc_info=True)
        # Log the full exception details
        import traceback
        logger.error(f"Full OpenAI error traceback:\n{traceback.format_exc()}")
    
    logger.info("Falling back to Gemini...")
    # Fallback to Gemini
    try:
        api_key = settings.GEMINI_API_KEY.get_secret_value()
        logger.info(f"Gemini API key configured (first 8 chars: {api_key[:8]}...)")
        genai.configure(api_key=api_key)
        logger.info("Making Gemini request...")
        model = genai.GenerativeModel("gemini-1.5-pro")
        gemini_response = model.generate_content(question)
        answer = gemini_response.text.strip()
        logger.info(f"Gemini request successful. Answer length: {len(answer)}")
        set_cached_answer(question, answer)
        return {"answer": answer, "cached": False, "provider": "gemini"}
    except Exception as e:
        logger.error(f"Gemini request failed with error: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"Full Gemini error traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="AI models are currently unavailable.") 