from fastapi import APIRouter, HTTPException, status

from app.schemas.candidate import (
    CandidateAnalyzeRequest,
    CandidateProfile,
)
from app.services.candidate_analyzer import (
    CandidateAnalysisError,
    analyze_candidate,
)


router = APIRouter(
    prefix="/api/candidate",
    tags=["Candidate"],
)


@router.post(
    "/analyze",
    response_model=CandidateProfile,
    status_code=status.HTTP_200_OK,
)
async def analyze_candidate_endpoint(
    request: CandidateAnalyzeRequest,
) -> CandidateProfile:
    """
    Analyze a candidate resume against a job description.
    """

    try:
        return analyze_candidate(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )

    except CandidateAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc