from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.services.resume_parser import (
    ResumeParsingError,
    parse_resume,
)


router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"],
)


@router.post(
    "/parse",
    status_code=status.HTTP_200_OK,
)
async def parse_resume_endpoint(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload and parse a candidate resume.

    Supported formats:
    - PDF
    - DOCX

    Maximum file size is controlled by MAX_RESUME_SIZE_MB.
    """
    settings = get_settings()

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    filename = file.filename.lower()

    if not (
        filename.endswith(".pdf")
        or filename.endswith(".docx")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported.",
        )

    max_size = settings.max_resume_size_mb * 1024 * 1024

    file_bytes = await file.read()

    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Resume file is too large. "
                f"Maximum allowed size is "
                f"{settings.max_resume_size_mb} MB."
            ),
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded resume is empty.",
        )

    try:
        resume_text = parse_resume(
            filename=file.filename,
            file_bytes=file_bytes,
        )

    except ResumeParsingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return {
        "status": "success",
        "filename": file.filename,
        "file_type": "pdf" if filename.endswith(".pdf") else "docx",
        "characters": len(resume_text),
        "text": resume_text,
    }