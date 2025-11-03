"""
Script management tools for audiobook generation.

This module provides tools for saving and managing generated scripts.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def _ai_save_script(chapter_id: str, script_text: str) -> dict:
    """
    Save generated script to database for a chapter.
    
    Args:
        chapter_id: UUID of the chapter
        script_text: The generated script text
    
    Returns:
        Dictionary with success status
    """
    try:
        from backend.db.session import SessionLocal
        from backend.models.chapter import Chapter
        
        db = SessionLocal()
        try:
            # Find the chapter
            chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            
            if not chapter:
                return {
                    "success": False,
                    "error": f"Chapter not found: {chapter_id}"
                }
            
            # Update the script
            chapter.script_text = script_text
            chapter.status = "scripting_complete"
            
            db.commit()
            
            logger.info(f"Saved script for chapter {chapter_id}, length: {len(script_text)} characters")
            
            return {
                "success": True,
                "chapter_id": str(chapter.id),
                "script_length": len(script_text)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error saving script for chapter {chapter_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
