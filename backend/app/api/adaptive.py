from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.adaptive import AdaptiveDecision
from app.schemas.evaluation import AnswerEvaluation

from app.services.adaptive_engine import (
    AdaptiveInterviewError,
    decide_next_action,
    generate_follow_up_question,
)


router = APIRouter(
    prefix="/api/adaptive",
    tags=["Adaptive Interview"],
)


class AdaptiveDecisionRequest(BaseModel):

    evaluation: AnswerEvaluation

    remaining_questions: int = Field(
        ...,
        ge=0,
        le=20,
    )

    current_difficulty: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )


class FollowUpQuestionRequest(BaseModel):

    original_question: dict

    answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    missing_topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )


@router.post(
    "/decision",
    response_model=AdaptiveDecision,
)
async def adaptive_decision(
    request: AdaptiveDecisionRequest,
) -> AdaptiveDecision:

    try:

        return decide_next_action(
            evaluation=request.evaluation,
            remaining_questions=request.remaining_questions,
            current_difficulty=request.current_difficulty,
        )

    except AdaptiveInterviewError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/follow-up",
)
async def adaptive_follow_up(
    request: FollowUpQuestionRequest,
):

    try:

        question = generate_follow_up_question(
            original_question=request.original_question,
            answer=request.answer,
            missing_topic=request.missing_topic,
        )

        return {
            "question": question
        }

    except AdaptiveInterviewError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc