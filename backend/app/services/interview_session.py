import json
import uuid

from sqlalchemy.orm import Session

from app.db.models import (
    AdaptiveDecision,
    Candidate,
    Interview,
    InterviewAnswer,
    InterviewQuestion,
    JobDescription,
)

from app.schemas.session import (
    AdaptiveHistory,
    InterviewAnswer as InterviewAnswerSchema,
    InterviewSession,
)


class InterviewSessionError(Exception):
    """
    Custom exception for interview session errors.
    """

    pass


def _question_to_dict(question: InterviewQuestion) -> dict:
    return {
        "id": question.question_id,
        "section": question.section,
        "question": question.question,
        "difficulty": question.difficulty,
        "expected_topics": (
            json.loads(question.expected_topics)
            if question.expected_topics
            else []
        ),
        "question_type": question.question_type,
        "parent_question_id": question.parent_question_id,
    }


def _session_to_schema(interview: Interview) -> InterviewSession:

    answers = []

    for question in interview.questions:

        for answer in question.answers:

            evaluation = None

            if answer.overall_score is not None:
                evaluation = {
                    "question_id": question.question_id,
                    "technical_score": answer.technical_score,
                    "relevance_score": answer.relevance_score,
                    "completeness_score": answer.completeness_score,
                    "communication_score": answer.communication_score,
                    "overall_score": answer.overall_score,
                    "strengths": (
                        json.loads(answer.strengths)
                        if answer.strengths
                        else []
                    ),
                    "weaknesses": (
                        json.loads(answer.weaknesses)
                        if answer.weaknesses
                        else []
                    ),
                    "feedback": answer.feedback or "",
                    "missing_topics": (
                        json.loads(answer.missing_topics)
                        if answer.missing_topics
                        else []
                    ),
                }

            answers.append(
                InterviewAnswerSchema(
                    question_id=question.question_id,
                    question=question.question,
                    answer=answer.answer,
                    evaluation=evaluation,
                )
            )

    adaptive_history = []

    for decision in interview.adaptive_history:

        adaptive_history.append(
            AdaptiveHistory(
                question_id=decision.question_id,
                action=decision.action,
                reason=decision.reason,
                next_difficulty=decision.next_difficulty,
                focus_topic=decision.focus_topic,
                follow_up_question=decision.follow_up_question,
            )
        )

    return InterviewSession(
        session_id=interview.session_id,
        candidate_name=interview.candidate.name,
        questions=[
            _question_to_dict(question)
            for question in interview.questions
        ],
        current_question_index=interview.current_question_index,
        answers=answers,
        adaptive_history=adaptive_history,
        status=interview.status,
    )


def create_session(
    db: Session,
    candidate_id: int,
    job_description_id: int,
    questions: list[dict],
) -> InterviewSession:
    """
    Create an interview session for an existing candidate and job description.
    """

    if not questions:
        raise InterviewSessionError(
            "At least one interview question is required."
        )

    # --------------------------------------------------
    # Find existing candidate
    # --------------------------------------------------

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if candidate is None:
        raise InterviewSessionError(
            "Candidate not found."
        )

    job_description = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_description_id
        )
        .first()
    )

    if job_description is None:
        raise InterviewSessionError(
            "Job description not found."
        )

    # --------------------------------------------------
    # Create interview
    # --------------------------------------------------

    session_id = str(uuid.uuid4())

    interview = Interview(
        session_id=session_id,
        candidate_id=candidate.id,
        job_description_id=job_description.id,
        status="active",
        current_question_index=0,
    )

    db.add(interview)
    db.flush()

    # --------------------------------------------------
    # Store questions
    # --------------------------------------------------

    for index, question in enumerate(questions):

        db_question = InterviewQuestion(
            interview_id=interview.id,
            question_id=question["id"],
            question_order=index,
            question=question["question"],
            section=question.get(
                "section",
                "General",
            ),
            difficulty=question.get(
                "difficulty",
                "Medium",
            ),
            question_type=question.get(
                "question_type",
                "main",
            ),
            parent_question_id=question.get(
                "parent_question_id"
            ),
            expected_topics=json.dumps(
                question.get(
                    "expected_topics",
                    [],
                )
            ),
        )

        db.add(db_question)

    db.commit()

    db.refresh(interview)

    return _session_to_schema(interview)


def get_session(
    db: Session,
    session_id: str,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    return _session_to_schema(interview)


def get_current_question(
    db: Session,
    session_id: str,
) -> dict | None:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    if (
        interview.current_question_index
        >= len(interview.questions)
    ):
        interview.status = "completed"
        db.commit()

        return None

    return _question_to_dict(
        interview.questions[
            interview.current_question_index
        ]
    )


def submit_answer(
    db: Session,
    session_id: str,
    answer: str,
) -> dict:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    if interview.status == "completed":
        raise InterviewSessionError(
            "Interview has already been completed."
        )

    if (
        interview.current_question_index
        >= len(interview.questions)
    ):
        interview.status = "completed"
        db.commit()

        raise InterviewSessionError(
            "No question is currently available."
        )

    current_question = interview.questions[
        interview.current_question_index
    ]

    db_answer = InterviewAnswer(
        question_id=current_question.id,
        answer=answer,
    )

    db.add(db_answer)

    interview.current_question_index += 1

    if (
        interview.current_question_index
        >= len(interview.questions)
    ):
        interview.status = "completed"
        next_question = None
    else:
        next_question = _question_to_dict(
            interview.questions[
                interview.current_question_index
            ]
        )

    db.commit()

    return {
        "status": interview.status,
        "message": "Answer submitted successfully.",
        "next_question": next_question,
    }


def store_evaluation(
    db: Session,
    session_id: str,
    question_id: str,
    evaluation: dict,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    db_question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id,
            InterviewQuestion.question_id
            == question_id,
        )
        .first()
    )

    if db_question is None:
        raise InterviewSessionError(
            "Question for evaluation was not found."
        )

    db_answer = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.question_id
            == db_question.id
        )
        .order_by(
            InterviewAnswer.id.desc()
        )
        .first()
    )

    if db_answer is None:
        raise InterviewSessionError(
            "Answer for the specified question was not found."
        )

    db_answer.technical_score = evaluation.get(
        "technical_score"
    )

    db_answer.relevance_score = evaluation.get(
        "relevance_score"
    )

    db_answer.completeness_score = evaluation.get(
        "completeness_score"
    )

    db_answer.communication_score = evaluation.get(
        "communication_score"
    )

    db_answer.overall_score = evaluation.get(
        "overall_score"
    )

    db_answer.strengths = json.dumps(
        evaluation.get("strengths", [])
    )

    db_answer.weaknesses = json.dumps(
        evaluation.get("weaknesses", [])
    )

    db_answer.feedback = evaluation.get(
        "feedback"
    )

    db_answer.missing_topics = json.dumps(
        evaluation.get("missing_topics", [])
    )

    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)


def store_adaptive_decision(
    db: Session,
    session_id: str,
    question_id: str,
    decision: dict,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    adaptive_decision = AdaptiveDecision(
        interview_id=interview.id,
        question_id=question_id,
        action=decision["action"],
        reason=decision["reason"],
        next_difficulty=decision[
            "next_difficulty"
        ],
        focus_topic=decision.get(
            "focus_topic"
        ),
        follow_up_question=decision.get(
            "follow_up_question"
        ),
    )

    db.add(adaptive_decision)
    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)


def add_follow_up_question(
    db: Session,
    session_id: str,
    question: str,
    parent_question_id: str,
    difficulty: str,
    focus_topic: str,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    follow_up_id = (
        f"{parent_question_id}-FU-"
        f"{len(interview.questions) + 1}"
    )

    db_question = InterviewQuestion(
        interview_id=interview.id,
        question_id=follow_up_id,
        question_order=interview.current_question_index,
        question=question,
        section="Adaptive Follow-up",
        difficulty=difficulty,
        question_type="follow_up",
        parent_question_id=parent_question_id,
        expected_topics=json.dumps(
            [focus_topic]
        ),
    )

    # Shift existing questions after the current position.
    for existing_question in interview.questions:

        if (
            existing_question.question_order
            >= interview.current_question_index
        ):
            existing_question.question_order += 1

    db.add(db_question)

    interview.status = "active"

    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)