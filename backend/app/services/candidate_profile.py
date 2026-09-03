import json

from sqlalchemy.orm import Session

from app.db.models import Candidate, CandidateProfile
from app.schemas.candidate import CandidateProfile as CandidateProfileSchema


class CandidateProfileError(Exception):
    pass


def create_candidate_profile(
    db: Session,
    candidate_name: str,
    resume_text: str,
    profile: CandidateProfileSchema,
) -> tuple[int, CandidateProfileSchema]:
    """
    Create a candidate and store their analyzed resume profile.
    """

    if not resume_text.strip():
        raise CandidateProfileError("Resume text cannot be empty.")

    candidate = Candidate(
        name=candidate_name.strip() or "Candidate"
    )

    db.add(candidate)
    db.flush()

    candidate_profile = CandidateProfile(
        candidate_id=candidate.id,
        resume_text=resume_text,

        education=json.dumps(profile.education),
        skills=json.dumps(profile.skills),
        experience=json.dumps(profile.experience),
        projects=json.dumps(profile.projects),
        matched_skills=json.dumps(profile.matched_skills),
        skill_gaps=json.dumps(profile.skill_gaps),
        experience_summary=profile.experience_summary,
    )

    db.add(candidate_profile)

    db.commit()

    return candidate.id, profile


def get_candidate_profile(
    db: Session,
    candidate_id: int,
) -> CandidateProfileSchema:
    """
    Retrieve a candidate profile from MySQL.
    """

    candidate_profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.candidate_id == candidate_id)
        .first()
    )

    if candidate_profile is None:
        raise CandidateProfileError(
            "Candidate profile not found."
        )

    return CandidateProfileSchema(
        candidate_name=(
            candidate_profile.candidate.name
            if candidate_profile.candidate
            else "Candidate"
        ),
        education=(
            json.loads(candidate_profile.education)
            if candidate_profile.education
            else []
        ),
        skills=(
            json.loads(candidate_profile.skills)
            if candidate_profile.skills
            else []
        ),
        experience=(
            json.loads(candidate_profile.experience)
            if candidate_profile.experience
            else []
        ),
        projects=(
            json.loads(candidate_profile.projects)
            if candidate_profile.projects
            else []
        ),
        matched_skills=(
            json.loads(candidate_profile.matched_skills)
            if candidate_profile.matched_skills
            else []
        ),
        skill_gaps=(
            json.loads(candidate_profile.skill_gaps)
            if candidate_profile.skill_gaps
            else []
        ),
        experience_summary=(
            candidate_profile.experience_summary or ""
        ),
    )