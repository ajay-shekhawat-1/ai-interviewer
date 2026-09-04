from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Candidate,
    Interview,
    InterviewAnswer,
    JobDescription,
)

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
    finish_session,
)

from app.services.interview_loop import (
    InterviewLoopError,
    process_answer,
)


router = APIRouter(
    prefix="/api/session",
    tags=["Interview Session"],
)


# =========================================================
# CREATE SESSION
# =========================================================

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


# =========================================================
# INTERVIEW HISTORY
# =========================================================

@router.get(
    "/history",
)
async def get_interview_history(
    db: Session = Depends(get_db),
):
    """
    Return previous interview sessions.

    Used by:
    - History page
    - Performance page
    """

    interviews = (
        db.query(Interview)
        .order_by(Interview.created_at.desc())
        .all()
    )

    history = []

    for interview in interviews:

        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == interview.candidate_id
            )
            .first()
        )

        job_description = None

        if interview.job_description_id:
            job_description = (
                db.query(JobDescription)
                .filter(
                    JobDescription.id
                    == interview.job_description_id
                )
                .first()
            )

        answers = (
            db.query(InterviewAnswer)
            .join(
                InterviewAnswer.question
            )
            .filter(
                InterviewAnswer.question.has(
                    interview_id=interview.id
                )
            )
            .all()
        )

        answered_questions = len(answers)

        def average_score(field):
            values = []

            for answer in answers:
                value = getattr(
                    answer,
                    field,
                    None,
                )

                if value is not None:
                    values.append(
                        float(value)
                    )

            if not values:
                return None

            return sum(values) / len(values)

        history.append(
            {
                "session_id": interview.session_id,

                "candidate_name": (
                    candidate.name
                    if candidate
                    else "Candidate"
                ),

                "job_title": (
                    job_description.job_title
                    if job_description
                    and job_description.job_title
                    else (
                        job_description.title
                        if job_description
                        else "Interview"
                    )
                ),

                "status": interview.status,

                "total_questions": len(
                    interview.questions
                ),

                "answered_questions":
                    answered_questions,

                "overall_score":
                    average_score(
                        "overall_score"
                    ),

                "technical_score":
                    average_score(
                        "technical_score"
                    ),

                "relevance_score":
                    average_score(
                        "relevance_score"
                    ),

                "completeness_score":
                    average_score(
                        "completeness_score"
                    ),

                "communication_score":
                    average_score(
                        "communication_score"
                    ),

                "created_at":
                    interview.created_at,
            }
        )

    return {
        "status": "success",
        "count": len(history),
        "interviews": history,
    }


# =========================================================
# FINISH INTERVIEW
# =========================================================

@router.post(
    "/{session_id}/finish",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
)
async def finish_interview(
    session_id: str,
    db: Session = Depends(get_db),
) -> InterviewSession:

    try:
        return finish_session(
            db=db,
            session_id=session_id,
        )

    except InterviewSessionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# =========================================================
# GET SINGLE SESSION
# =========================================================

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


# =========================================================
# CURRENT QUESTION
# =========================================================

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


# =========================================================
# SUBMIT ANSWER
# =========================================================

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


# =========================================================
# PROCESS ANSWER
# =========================================================

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