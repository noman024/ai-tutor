from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.app.services.ai_cache import get_cached_answer, set_cached_answer
from backend.app.core.config import get_settings
from fastapi.security import OAuth2PasswordBearer
from backend.app.api.auth import get_current_user
from backend.app.models import User, File as FileModel
from backend.app.services.pptx_service import PPTXService
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from openai import OpenAI
import google.generativeai as genai
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger("ai_teacher")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AskRequest(BaseModel):
    question: str
    slide_deck_id: int | None = None  # Optional slide deck ID

@router.post("/ask")
def ask_ai(
    data: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = data.question.strip()
    slide_deck_id = data.slide_deck_id
    
    logger.info(f"Received question from user {current_user.email}: {question}")
    if slide_deck_id:
        logger.info(f"Using slide deck ID: {slide_deck_id}")
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    # Check cache (include slide_deck_id in cache key if provided)
    cache_key = f"{question}_{slide_deck_id}" if slide_deck_id else question
    cached = get_cached_answer(cache_key)
    if cached:
        logger.info(f"Cache hit for question: {question}")
        return {"answer": cached, "cached": True, "provider": "cache"}
    
    # Get slide deck content if slide_deck_id is provided
    slide_content = None
    if slide_deck_id:
        try:
            # Verify the slide deck belongs to the user
            slide_deck = db.query(FileModel).filter(
                FileModel.id == slide_deck_id,
                FileModel.user_id == current_user.id,
                FileModel.converted_pptx_path.isnot(None)
            ).first()
            
            if not slide_deck:
                raise HTTPException(
                    status_code=404,
                    detail="Slide deck not found or not accessible"
                )
            
            # Extract and format slide content
            slides_content = PPTXService.extract_text_from_pptx(slide_deck.converted_pptx_path)
            slide_content = PPTXService.format_slides_for_prompt(slides_content)
            logger.info(f"Successfully extracted content from slide deck {slide_deck_id}")
            
        except Exception as e:
            logger.error(f"Error processing slide deck {slide_deck_id}: {str(e)}", exc_info=True)
            # Continue without slide content if there's an error
            slide_content = None
    
    # Prepare the prompt with slide content if available
    if slide_content:
        prompt = f"""You are an AI tutor helping a student understand their course material. 
Use the following slide deck content as your primary reference to answer the question.
If the answer cannot be fully derived from the slides, you may supplement with your knowledge,
but clearly indicate which parts come from the slides vs. your general knowledge.

{slide_content}

Student's question: {question}

Please provide a clear, educational response that:
1. Primarily uses information from the slides
2. Clearly indicates which parts come from the slides
3. Only supplements with your knowledge if necessary
4. Maintains a helpful, tutoring tone"""
    else:
        prompt = f"""You are an AI tutor helping a student. Please answer their question in a clear, educational manner.

Student's question: {question}"""
    
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
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024  # Increased for longer responses with slide content
        }
        logger.info(f"Making OpenAI request with data: {request_data}")
        
        # Make the request using the new client
        response = client.chat.completions.create(**request_data)
        
        # Log the raw response
        logger.info(f"OpenAI raw response: {response}")
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"OpenAI request successful. Answer length: {len(answer)}")
        set_cached_answer(cache_key, answer)
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
        gemini_response = model.generate_content(prompt)
        answer = gemini_response.text.strip()
        logger.info(f"Gemini request successful. Answer length: {len(answer)}")
        set_cached_answer(cache_key, answer)
        return {"answer": answer, "cached": False, "provider": "gemini"}
    except Exception as e:
        logger.error(f"Gemini request failed with error: {str(e)}", exc_info=True)
        import traceback
        logger.error(f"Full Gemini error traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="AI models are currently unavailable.") 