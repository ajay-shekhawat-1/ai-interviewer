from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.jd import (
    CreateJDRequest,
    JDAnalyzeRequest,
    JDProfile,
    JDResponse,
)
from app.services.jd_analyzer import (
    JDAnalysisError,
    analyze_job_description,
)
from app.services.job_description import (
    JobDescriptionError,
    create_job_description,
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
        return analyze_job_description(request.job_description)

    except JDAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/create",
    response_model=JDResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_jd(
    request: CreateJDRequest,
    db: Session = Depends(get_db),
):
    try:
        profile = analyze_job_description(request.raw_text)

        if not isinstance(profile, JDProfile):
            raise JobDescriptionError(
                "JD analyzer returned an invalid profile."
            )

        job_description_id = create_job_description(
            db=db,
            raw_text=request.raw_text,
            profile=profile,
        )

        return JDResponse(
            job_description_id=job_description_id,
            profile=profile,
        )

    except JobDescriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"JD processing failed: {str(exc)}",
        ) from exc