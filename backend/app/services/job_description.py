import json

from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jd import JDProfile


class JobDescriptionError(Exception):
    pass


def create_job_description(
    db: Session,
    raw_text: str,
    profile: JDProfile,
) -> int:

    if not raw_text.strip():
        raise JobDescriptionError(
            "Job description cannot be empty."
        )

    job_description = JobDescription(
        title=profile.job_title or "Job Position",
        raw_text=raw_text,

        job_title=profile.job_title,
        experience_level=profile.experience_level,

        required_skills=json.dumps(
            profile.required_skills
        ),

        preferred_skills=json.dumps(
            profile.preferred_skills
        ),

        responsibilities=json.dumps(
            profile.responsibilities
        ),

        technical_topics=json.dumps(
            profile.technical_topics
        ),
    )

    db.add(job_description)
    db.commit()
    db.refresh(job_description)

    return job_description.id
import json

from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jd import JDProfile


def get_job_description_profile(
    db: Session,
    job_description_id: int,
) -> JDProfile:
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_description_id)
        .first()
    )

    if job_description is None:
        raise JobDescriptionError("Job description not found.")

    return JDProfile(
        job_title=job_description.job_title or job_description.title,
        experience_level=job_description.experience_level or "",
        required_skills=json.loads(job_description.required_skills)
        if job_description.required_skills
        else [],
        preferred_skills=json.loads(job_description.preferred_skills)
        if job_description.preferred_skills
        else [],
        responsibilities=json.loads(job_description.responsibilities)
        if job_description.responsibilities
        else [],
        technical_topics=json.loads(job_description.technical_topics)
        if job_description.technical_topics
        else [],
    )