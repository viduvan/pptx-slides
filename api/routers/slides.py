"""
Slides Router — Endpoints for generating, editing, previewing, and downloading slides.
"""
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..models.schemas import (
    GenerateRequest,
    GenerateResponse,
    EditRequest,
    PreviewResponse,
    SlideData,
    UndoRequest,
)
from ..services import llm_service, slide_service
from ..core.session_manager import session_manager

logger = logging.getLogger("odin_api.routers.slides")
router = APIRouter(prefix="/api/slides", tags=["Slides"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_slides(request: GenerateRequest):
    """
    Generate a new set of slides from a prompt.
    Optionally provide word_content (from uploaded docx) to base the slides on.
    """
    try:
        slides = await llm_service.generate_slides(
            prompt=request.prompt,
            word_content=request.word_content,
            existing_slides=[],
        )

        # Create session
        template_path = slide_service.get_template_path(request.template_name)
        session = session_manager.create_session(
            slides=slides,
            word_content=request.word_content,
            template_name=str(template_path),
        )

        return GenerateResponse(
            session_id=session.session_id,
            slides=[SlideData(**s) for s in slides],
            message=f"Generated {len(slides)} slides successfully",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating slides: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate slides: {e}")


@router.post("/edit", response_model=GenerateResponse)
async def edit_slides(request: EditRequest):
    """
    Edit existing slides using a prompt.
    The LLM will modify, add, or remove slides based on the instruction.
    """
    session = session_manager.get_session(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Get LLM response for edits
        new_slides = await llm_service.generate_slides(
            prompt=request.prompt,
            word_content=session.word_content,
            existing_slides=session.slides.copy(),
        )

        # Merge new slides with existing
        merged = slide_service.merge_slides(
            existing_slides=session.slides.copy(),
            new_slides=new_slides,
        )

        # Update session
        session_manager.update_slides(request.session_id, merged)

        return GenerateResponse(
            session_id=request.session_id,
            slides=[SlideData(**s) for s in merged],
            message=f"Slides updated. Now {len(merged)} slides total.",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error editing slides: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to edit slides: {e}")


@router.get("/{session_id}/preview", response_model=PreviewResponse)
async def preview_slides(session_id: str):
    """
    Get slide data for frontend preview rendering.
    Returns JSON representation of all slides.
    """
    session = session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    preview_data = slide_service.slides_to_preview(session.slides)
    return PreviewResponse(
        session_id=session_id,
        slides=[SlideData(**s) for s in preview_data],
        total_slides=len(preview_data),
        created_at=session.created_at,
    )


@router.get("/{session_id}/download")
async def download_slides(session_id: str):
    """
    Generate and download the PPTX file for the current session.
    """
    session = session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        template_path = session.template_name
        output_path = slide_service.create_pptx(
            slides=session.slides,
            template_path=template_path,
            output_path=None,  # auto-generate temp path
        )

        return FileResponse(
            path=str(output_path),
            filename="presentation.pptx",
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    except Exception as e:
        logger.error(f"Error creating PPTX: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create PPTX file: {e}")


@router.post("/{session_id}/undo", response_model=GenerateResponse)
async def undo_slides(session_id: str):
    """
    Undo the last edit and revert to the previous version.
    """
    session = session_manager.undo(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return GenerateResponse(
        session_id=session_id,
        slides=[SlideData(**s) for s in session.slides],
        message="Reverted to previous version",
    )
