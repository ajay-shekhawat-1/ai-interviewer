from sqlalchemy.orm import Session

from app.schemas.candidate import CandidateProfile
from app.services.candidate_profile import create_candidate_profile
from app.services.candidate_analyzer import analyze_candidate


class CandidatePipelineError(Exception):
    pass


def process_candidate_resume(
    db: Session,
    candidate_name: str,
    resume_text: str,
    job_description: str,
) -> tuple[int, CandidateProfile]:
    """
    Complete candidate processing pipeline:

    Resume text
        ↓
    Candidate Analyzer
        ↓
    Candidate Profile
        ↓
    MySQL
    """

    if not resume_text.strip():
        raise CandidatePipelineError(
            "Resume text cannot be empty."
        )

    if not job_description.strip():
        raise CandidatePipelineError(
            "Job description cannot be empty."
        )

    try:
        profile = analyze_candidate(
            resume_text=resume_text,
            job_description=job_description,
        )

    except Exception as exc:
        raise CandidatePipelineError(
            f"Candidate analysis failed: {str(exc)}"
        ) from exc

    if not isinstance(profile, CandidateProfile):
        raise CandidatePipelineError(
            "Candidate analyzer returned an invalid profile."
        )

    try:
        candidate_id, saved_profile = create_candidate_profile(
            db=db,
            candidate_name=candidate_name,
            resume_text=resume_text,
            profile=profile,
        )

    except Exception as exc:
        raise CandidatePipelineError(
            f"Failed to save candidate profile: {str(exc)}"
        ) from exc

    return candidate_id, saved_profile