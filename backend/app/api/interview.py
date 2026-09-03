from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.interview_start import (
    StartInterviewRequest,
    StartInterviewResponse,
)
from app.services.interview_start import (
    InterviewStartError,
    start_interview,
)


router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"],
)


@router.post(
    "/start",
    response_model=StartInterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_interview_endpoint(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
) -> StartInterviewResponse:

    try:
        return start_interview(
            db=db,
            candidate_id=request.candidate_id,
            job_description_id=request.job_description_id,
        )

    except InterviewStartError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc