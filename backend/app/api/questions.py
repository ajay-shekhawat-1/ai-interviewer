from fastapi import APIRouter, HTTPException, status

from app.schemas.question import (
    QuestionGenerationRequest,
    QuestionSet,
)

from app.services.question_generator import (
    QuestionGenerationError,
    generate_questions,
)


router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"],
)


@router.post(
    "/generate",
    response_model=QuestionSet,
    status_code=status.HTTP_200_OK,
)
async def generate_questions_endpoint(
    request: QuestionGenerationRequest,
) -> QuestionSet:

    try:

        return generate_questions(
            jd_profile=request.jd_profile,
            candidate_profile=request.candidate_profile,
            interview_blueprint=request.interview_blueprint,
        )

    except QuestionGenerationError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc