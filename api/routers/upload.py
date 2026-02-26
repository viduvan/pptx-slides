"""
Upload Router — Endpoints for uploading and processing Word and PDF documents.
"""
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from ..models.schemas import UploadResponse
from ..services import llm_service, document_service
from ..core.config import settings

logger = logging.getLogger("odin_api.routers.upload")
router = APIRouter(prefix="/api/upload", tags=["Upload"])

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}


@router.post("/docx", response_model=UploadResponse)
async def upload_docx(file: UploadFile = File(...)):
    """Upload a Word document (.docx). Kept for backward compatibility."""
    return await _process_upload(file, allowed_exts={".docx"})


@router.post("/document", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (.docx or .pdf).
    The document will be read and optionally summarized if it's too large.
    Returns the extracted text content to be used in slide generation.
    """
    return await _process_upload(file, allowed_exts=SUPPORTED_EXTENSIONS)


async def _process_upload(file: UploadFile, allowed_exts: set[str]) -> UploadResponse:
    """Common upload processing for both docx and pdf."""
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(allowed_exts))}"
        )

    # Save uploaded file to temp directory
    temp_path = settings.TEMP_DIR / f"{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        # Process the document (read + optional summarization)
        word_content, was_summarized = await document_service.process_document(
            file_path=temp_path,
            summarize_fn=llm_service.summarize_content,
        )
        word_count = len(word_content.split())

        return UploadResponse(
            word_content=word_content,
            word_count=word_count,
            was_summarized=was_summarized,
            message=(
                f"Document processed successfully. {word_count} words"
                + (" (summarized)" if was_summarized else "")
                + "."
            ),
        )

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

