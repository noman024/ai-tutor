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
import base64
from fastapi.responses import FileResponse
import mimetypes
import os

router = APIRouter()
settings = get_settings()
logger = logging.getLogger("ai_teacher")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AskRequest(BaseModel):
    question: str
    slide_deck_id: int | None = None  # Optional slide deck ID

class ExplainSlideRequest(BaseModel):
    slide_deck_id: int
    slide_number: int

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

@router.get("/slides/{slide_deck_id}")
def get_slide_deck_content(
    slide_deck_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return a list of slides (number, content, and/or image availability) for a given slide deck, if the user owns it.
    """
    slide_deck = db.query(FileModel).filter(
        FileModel.id == slide_deck_id,
        FileModel.user_id == current_user.id,
        FileModel.converted_pptx_path.isnot(None)
    ).first()
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found or not accessible")
    try:
        slides_content = PPTXService.extract_text_from_pptx(slide_deck.converted_pptx_path)
        slides_images = PPTXService.extract_images_from_pptx(slide_deck.converted_pptx_path)
        slides = []
        max_slide = max(
            [s["slide_number"] for s in slides_content] + [s["slide_number"] for s in slides_images],
            default=0
        )
        for idx in range(1, max_slide + 1):
            text_slide = next((s for s in slides_content if s["slide_number"] == idx), None)
            image_slide = next((s for s in slides_images if s["slide_number"] == idx), None)
            slide_obj = {"slide_number": idx}
            if text_slide:
                slide_obj["content"] = text_slide["content"]
            if image_slide:
                slide_obj["image_available"] = True
            slides.append(slide_obj)
        return {"slides": slides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract slides: {str(e)}")

@router.get("/slide-image/{slide_deck_id}/{slide_number}")
def get_slide_image(
    slide_deck_id: int,
    slide_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return the raw image for a given slide (if available).
    """
    slide_deck = db.query(FileModel).filter(
        FileModel.id == slide_deck_id,
        FileModel.user_id == current_user.id,
        FileModel.converted_pptx_path.isnot(None)
    ).first()
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found or not accessible")
    slides_images = PPTXService.extract_images_from_pptx(slide_deck.converted_pptx_path)
    image_info = next((img for img in slides_images if img["slide_number"] == slide_number), None)
    if not image_info:
        logger.error(f"Image not found for slide {slide_number} in deck {slide_deck_id}")
        raise HTTPException(status_code=404, detail="Image not found for this slide")
    image_path = image_info["image_path"]
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    if not os.path.exists(image_path):
        logger.error(f"Image file does not exist: {image_path}")
        raise HTTPException(status_code=404, detail="Image file not found on server")
    return FileResponse(image_path, media_type=mime_type)

@router.post("/explain-slide")
def explain_slide(
    data: ExplainSlideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    slide_deck_id = data.slide_deck_id
    slide_number = data.slide_number
    # Verify deck ownership and existence
    slide_deck = db.query(FileModel).filter(
        FileModel.id == slide_deck_id,
        FileModel.user_id == current_user.id,
        FileModel.converted_pptx_path.isnot(None)
    ).first()
    if not slide_deck:
        raise HTTPException(status_code=404, detail="Slide deck not found or not accessible")
    # Extract slides (text)
    slides_content = PPTXService.extract_text_from_pptx(slide_deck.converted_pptx_path)
    slide = next((s for s in slides_content if s["slide_number"] == slide_number), None)
    slide_text = slide["content"] if slide else ""
    # If text is present, use text-based prompt
    if slide_text.strip():
        prompt = f"""You are an expert teacher. Explain the following slide to a student in a clear, engaging, and educational way. Use analogies, examples, and break down complex ideas. Only use the content provided below.\n\nSlide Content:\n{slide_text}\n"""
        # Try OpenAI first
        try:
            api_key = settings.OPENAI_API_KEY.get_secret_value()
            client = OpenAI(api_key=api_key)
            request_data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 512
            }
            response = client.chat.completions.create(**request_data)
            explanation = response.choices[0].message.content.strip()
            return {"explanation": explanation, "provider": "openai"}
        except Exception:
            pass
        # Fallback to Gemini
        try:
            api_key = settings.GEMINI_API_KEY.get_secret_value()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            gemini_response = model.generate_content(prompt)
            explanation = gemini_response.text.strip()
            return {"explanation": explanation, "provider": "gemini"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI models are currently unavailable: {str(e)}")
    # If no text, try image-based vision model
    # Extract image for this slide
    image_bytes, mime_type = PPTXService.extract_image_from_slide(slide_deck.converted_pptx_path, slide_number)
    if not image_bytes:
        logger.error(f"No image found for slide {slide_number} in deck {slide_deck_id}")
        raise HTTPException(status_code=400, detail="Slide is empty (no text or image)")
    # OpenAI Vision (primary)
    try:
        api_key = settings.OPENAI_API_KEY.get_secret_value()
        client = OpenAI(api_key=api_key)
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        # Use correct image MIME type in the prompt
        openai_image_type = 'image/png' if mime_type == 'image/png' else 'image/jpeg'
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": vision_prompt},
                        {"type": "input_image", "image_url": f"data:{openai_image_type};base64,{base64_image}"},
                    ],
                }
            ],
        )
        explanation = response.output_text.strip()
        return {"explanation": explanation, "provider": "openai-vision"}
    except Exception as e:
        logger.error(f"OpenAI Vision failed: {str(e)}")
        pass
    # Gemini Vision (fallback)
    try:
        api_key = settings.GEMINI_API_KEY.get_secret_value()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro-vision")
        from google.genai import types
        gemini_response = model.generate_content([
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            vision_prompt
        ])
        explanation = gemini_response.text.strip()
        return {"explanation": explanation, "provider": "gemini-vision"}
    except Exception as e:
        logger.error(f"Gemini Vision failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI models are currently unavailable for image slides: {str(e)}") 