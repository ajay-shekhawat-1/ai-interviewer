from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.evaluation import (
    AnswerEvaluation,
    InterviewReport,
)

from app.services.answer_evaluator import (
    AnswerEvaluationError,
    evaluate_answer,
)

from app.services.interview_report import (
    InterviewReportError,
    generate_interview_report,
)


router = APIRouter(
    prefix="/api/evaluation",
    tags=["Answer Evaluation"],
)


class EvaluateAnswerRequest(BaseModel):
    """
    Request for evaluating one interview answer.
    """

    question: dict = Field(
        ...,
        description="Interview question object.",
    )

    answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Candidate's answer.",
    )


@router.post(
    "/answer",
    response_model=AnswerEvaluation,
    status_code=status.HTTP_200_OK,
)
async def evaluate_answer_endpoint(
    request: EvaluateAnswerRequest,
) -> AnswerEvaluation:

    try:

        return evaluate_answer(
            question=request.question,
            answer=request.answer,
        )

    except AnswerEvaluationError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/report/{session_id}",
    response_model=InterviewReport,
    status_code=status.HTTP_200_OK,
)
async def get_interview_report(
    session_id: str,
    db: Session = Depends(get_db),
) -> InterviewReport:

    try:

        return generate_interview_report(
            db=db,
            session_id=session_id,
        )

    except InterviewReportError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc