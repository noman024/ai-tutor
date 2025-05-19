from pptx import Presentation
from typing import List, Dict
import logging

logger = logging.getLogger("pptx_service")

class PPTXService:
    @staticmethod
    def extract_text_from_pptx(pptx_path: str) -> List[Dict[str, str]]:
        """
        Extract text content from a PPTX file, including slide numbers and content.
        Returns a list of dictionaries containing slide number and content.
        """
        try:
            prs = Presentation(pptx_path)
            slides_content = []
            
            for idx, slide in enumerate(prs.slides, 1):
                slide_text = []
                
                # Extract text from shapes (textboxes, etc.)
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text.strip())
                
                # If slide has any text, add it to the content
                if slide_text:
                    slides_content.append({
                        "slide_number": idx,
                        "content": "\n".join(slide_text)
                    })
            
            logger.info(f"Successfully extracted text from {len(slides_content)} slides in {pptx_path}")
            return slides_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PPTX {pptx_path}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def format_slides_for_prompt(slides_content: List[Dict[str, str]]) -> str:
        """
        Format slide content into a prompt-friendly string.
        """
        formatted_content = "Slide Deck Content:\n\n"
        for slide in slides_content:
            formatted_content += f"Slide {slide['slide_number']}:\n{slide['content']}\n\n"
        return formatted_content.strip() 