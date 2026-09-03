from sqlalchemy.orm import Session

from app.schemas.evaluation import InterviewReport
from app.services.interview_session import get_session


class InterviewReportError(Exception):
    """
    Custom exception for interview report errors.
    """

    pass


def generate_interview_report(
    db: Session,
    session_id: str,
) -> InterviewReport:

    session = get_session(
        db=db,
        session_id=session_id,
    )

    # Report can only be generated after interview completion.
    if session.status != "completed":
        raise InterviewReportError(
            "Interview must be completed before generating the final report."
        )

    if not session.answers:
        raise InterviewReportError(
            "No answers are available for this interview."
        )

    technical_scores = []
    relevance_scores = []
    completeness_scores = []
    communication_scores = []
    overall_scores = []

    strengths = []
    weaknesses = []
    skill_gaps = []

    question_results = []

    for answer in session.answers:

        evaluation = answer.evaluation

        # Skip answers that were not evaluated.
        if not evaluation:
            continue

        technical_scores.append(
            float(evaluation.get("technical_score", 0))
        )

        relevance_scores.append(
            float(evaluation.get("relevance_score", 0))
        )

        completeness_scores.append(
            float(evaluation.get("completeness_score", 0))
        )

        communication_scores.append(
            float(evaluation.get("communication_score", 0))
        )

        overall_scores.append(
            float(evaluation.get("overall_score", 0))
        )

        strengths.extend(
            evaluation.get("strengths", [])
        )

        weaknesses.extend(
            evaluation.get("weaknesses", [])
        )

        skill_gaps.extend(
            evaluation.get("missing_topics", [])
        )

        question_results.append(
            {
                "question_id": answer.question_id,
                "question": answer.question,
                "answer": answer.answer,
                "evaluation": evaluation,
            }
        )

    if not overall_scores:
        raise InterviewReportError(
            "No evaluated answers are available."
        )

    def average(values: list[float]) -> float:
        return round(
            sum(values) / len(values),
            2,
        )

    technical_score = average(technical_scores)
    relevance_score = average(relevance_scores)
    completeness_score = average(completeness_scores)
    communication_score = average(communication_scores)
    overall_score = average(overall_scores)

    return InterviewReport(
        candidate_name=session.candidate_name,

        total_questions=len(session.questions),

        answered_questions=len(session.answers),

        technical_score=technical_score,

        relevance_score=relevance_score,

        completeness_score=completeness_score,

        communication_score=communication_score,

        overall_score=overall_score,

        strengths=list(
            dict.fromkeys(strengths)
        )[:20],

        weaknesses=list(
            dict.fromkeys(weaknesses)
        )[:20],

        skill_gaps=list(
            dict.fromkeys(skill_gaps)
        )[:20],

        recommendation=_generate_recommendation(
            overall_score
        ),

        summary=_generate_summary(
            candidate_name=session.candidate_name,
            overall_score=overall_score,
            technical_score=technical_score,
            communication_score=communication_score,
        ),

        question_results=question_results,
    )


def _generate_recommendation(
    overall_score: float,
) -> str:

    if overall_score >= 8:
        return (
            "Strong performance. Candidate is recommended "
            "for the next interview round."
        )

    if overall_score >= 6:
        return (
            "Good performance. Candidate can be considered "
            "for the next interview round."
        )

    if overall_score >= 4:
        return (
            "Moderate performance. Candidate may require "
            "additional evaluation."
        )

    return (
        "Weak performance. Candidate is not recommended "
        "for the next round based on this interview."
    )


def _generate_summary(
    candidate_name: str,
    overall_score: float,
    technical_score: float,
    communication_score: float,
) -> str:

    return (
        f"{candidate_name} achieved an overall interview "
        f"score of {overall_score}/10. "
        f"Technical performance was {technical_score}/10 "
        f"and communication performance was "
        f"{communication_score}/10."
    )