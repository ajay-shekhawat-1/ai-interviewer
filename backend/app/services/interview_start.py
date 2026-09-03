from sqlalchemy.orm import Session

from app.schemas.interview_start import StartInterviewResponse
from app.services.candidate_profile import (
    CandidateProfileError,
    get_candidate_profile,
)
from app.services.interview_blueprint import (
    InterviewBlueprintError,
    generate_interview_blueprint,
)
from app.services.interview_session import (
    InterviewSessionError,
    create_session,
)
from app.services.job_description import (
    JobDescriptionError,
    get_job_description_profile,
)
from app.services.question_generator import (
    QuestionGenerationError,
    generate_questions,
)


class InterviewStartError(Exception):
    pass


def start_interview(
    db: Session,
    candidate_id: int,
    job_description_id: int,
) -> StartInterviewResponse:

    try:
        # 1. Load candidate profile
        candidate_profile = get_candidate_profile(
            db=db,
            candidate_id=candidate_id,
        )

        # 2. Load job description profile
        jd_profile = get_job_description_profile(
            db=db,
            job_description_id=job_description_id,
        )

        # 3. Generate interview blueprint
        blueprint = generate_interview_blueprint(
            jd_profile=jd_profile,
            candidate_profile=candidate_profile,
        )

        # 4. Generate interview questions
        question_set = generate_questions(
            jd_profile=jd_profile.model_dump(),
            candidate_profile=candidate_profile.model_dump(),
            interview_blueprint=blueprint.model_dump(),
        )

        # 5. Create database interview session
        session = create_session(
            db=db,
            candidate_id=candidate_id,
            job_description_id=job_description_id,
            questions=[
                question.model_dump()
                for question in question_set.questions
            ],
        )

        return StartInterviewResponse(
            session=session,
            blueprint=blueprint,
        )

    except (
        CandidateProfileError,
        JobDescriptionError,
        InterviewBlueprintError,
        QuestionGenerationError,
        InterviewSessionError,
    ) as exc:
        raise InterviewStartError(str(exc)) from exc

    except Exception as exc:
        raise InterviewStartError(
            f"Failed to start interview: {str(exc)}"
        ) from exc