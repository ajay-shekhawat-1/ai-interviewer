from fastapi import APIRouter, HTTPException, status

from app.schemas.jd import JDAnalyzeRequest, JDProfile
from app.services.jd_analyzer import (
    JDAnalysisError,
    analyze_job_description,
)


router = APIRouter(
    prefix="/api/jd",
    tags=["Job Description"],
)


@router.post(
    "/analyze",
    response_model=JDProfile,
    status_code=status.HTTP_200_OK,
)
async def analyze_jd(
    request: JDAnalyzeRequest,
) -> JDProfile:
    """
    Analyze a job description and return a structured JD profile.
    """

    try:
        return analyze_job_description(
            request.job_description
        )

    except JDAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc