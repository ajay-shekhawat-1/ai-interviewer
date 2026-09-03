from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.session import (
    CreateInterviewSessionRequest,
    InterviewSession,
    SubmitAnswerRequest,
)

from app.services.interview_session import (
    InterviewSessionError,
    create_session,
    get_current_question,
    get_session,
    submit_answer,
)

from app.services.interview_loop import (
    InterviewLoopError,
    process_answer,
)


router = APIRouter(
    prefix="/api/session",
    tags=["Interview Session"],
)


@router.post(
    "/create",
    response_model=InterviewSession,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview_session(
    request: CreateInterviewSessionRequest,
    db: Session = Depends(get_db),
) -> InterviewSession:

    try:
        return create_session(
            db=db,
            candidate_id=request.candidate_id,
            job_description_id=request.job_description_id,
            questions=request.questions,
        )

    except InterviewSessionError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{session_id}",
    response_model=InterviewSession,
)
async def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> InterviewSession:

    try:

        return get_session(
            db=db,
            session_id=session_id,
        )

    except InterviewSessionError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{session_id}/current-question",
)
async def get_current_interview_question(
    session_id: str,
    db: Session = Depends(get_db),
):

    try:

        question = get_current_question(
            db=db,
            session_id=session_id,
        )

        return {
            "question": question
        }

    except InterviewSessionError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{session_id}/answer",
)
async def submit_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
):

    try:

        return submit_answer(
            db=db,
            session_id=session_id,
            answer=request.answer,
        )

    except InterviewSessionError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{session_id}/process-answer",
)
async def process_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
):

    try:

        return process_answer(
            db=db,
            session_id=session_id,
            answer=request.answer,
        )

    except InterviewLoopError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc