from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.candidate import CandidateProfile
from app.schemas.candidate_profile import (
    CandidateProfileResponse,
    CreateCandidateProfileRequest,
    ProcessCandidateRequest,
)
from app.services.candidate_pipeline import (
    CandidatePipelineError,
    process_candidate_resume,
)
from app.services.candidate_profile import (
    CandidateProfileError,
    create_candidate_profile,
)
from app.services.resume_parser import parse_resume


router = APIRouter(
    prefix="/api/candidate-profile",
    tags=["Candidate Profile"],
)


@router.post(
    "/process",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_candidate(
    request: ProcessCandidateRequest,
    db: Session = Depends(get_db),
):
    try:
        candidate_id, profile = process_candidate_resume(
            db=db,
            candidate_name=request.candidate_name,
            resume_text=request.resume_text,
            job_description=request.job_description,
        )

        return CandidateProfileResponse(
            candidate_id=candidate_id,
            candidate_name=profile.candidate_name,
            profile=profile.model_dump(),
        )

    except CandidatePipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/create",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    request: CreateCandidateProfileRequest,
    db: Session = Depends(get_db),
):
    try:
        profile = CandidateProfile.model_validate(
            request.profile
        )

        candidate_id, saved_profile = create_candidate_profile(
            db=db,
            candidate_name=request.candidate_name,
            resume_text=request.resume_text,
            profile=profile,
        )

        return CandidateProfileResponse(
            candidate_id=candidate_id,
            candidate_name=request.candidate_name,
            profile=saved_profile.model_dump(),
        )

    except CandidateProfileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/upload-resume",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    candidate_name: str = Form("Candidate"),
    job_description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload PDF/DOCX resume, extract text, analyze candidate,
    and store the candidate profile in MySQL.
    """

    allowed_extensions = {".pdf", ".docx"}

    file_extension = Path(
        file.filename or ""
    ).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX resume files are supported.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required.",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded resume is empty.",
            )

        resume_text = parse_resume(
            file_bytes=file_bytes,
            filename=file.filename,
        )

        candidate_id, profile = process_candidate_resume(
            db=db,
            candidate_name=candidate_name,
            resume_text=resume_text,
            job_description=job_description,
        )

        return CandidateProfileResponse(
            candidate_id=candidate_id,
            candidate_name=profile.candidate_name,
            profile=profile.model_dump(),
        )

    except CandidatePipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume processing failed: {str(exc)}",
        ) from exc