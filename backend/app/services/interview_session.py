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


# =========================================================
# QUESTION → DICT
# =========================================================

def _question_to_dict(
    question: InterviewQuestion,
) -> dict:

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


# =========================================================
# INTERVIEW → SCHEMA
# =========================================================

def _session_to_schema(
    interview: Interview,
) -> InterviewSession:

    answers = []

    for question in interview.questions:

        for answer in question.answers:

            evaluation = None

            if answer.overall_score is not None:

                evaluation = {
                    "question_id":
                        question.question_id,

                    "technical_score":
                        answer.technical_score,

                    "relevance_score":
                        answer.relevance_score,

                    "completeness_score":
                        answer.completeness_score,

                    "communication_score":
                        answer.communication_score,

                    "overall_score":
                        answer.overall_score,

                    "strengths": (
                        json.loads(
                            answer.strengths
                        )
                        if answer.strengths
                        else []
                    ),

                    "weaknesses": (
                        json.loads(
                            answer.weaknesses
                        )
                        if answer.weaknesses
                        else []
                    ),

                    "feedback":
                        answer.feedback or "",

                    "missing_topics": (
                        json.loads(
                            answer.missing_topics
                        )
                        if answer.missing_topics
                        else []
                    ),
                }

            answers.append(
                InterviewAnswerSchema(
                    question_id=
                        question.question_id,

                    question=
                        question.question,

                    answer=
                        answer.answer,

                    evaluation=
                        evaluation,
                )
            )

    adaptive_history = []

    for decision in interview.adaptive_history:

        adaptive_history.append(
            AdaptiveHistory(
                question_id=
                    decision.question_id,

                action=
                    decision.action,

                reason=
                    decision.reason,

                next_difficulty=
                    decision.next_difficulty,

                focus_topic=
                    decision.focus_topic,

                follow_up_question=
                    decision.follow_up_question,
            )
        )

    return InterviewSession(
        session_id=
            interview.session_id,

        candidate_name=
            interview.candidate.name,

        questions=[
            _question_to_dict(question)
            for question in interview.questions
        ],

        current_question_index=
            interview.current_question_index,

        answers=
            answers,

        adaptive_history=
            adaptive_history,

        status=
            interview.status,
    )


# =========================================================
# CREATE SESSION
# =========================================================

def create_session(
    db: Session,
    candidate_id: int,
    job_description_id: int,
    questions: list[dict],
) -> InterviewSession:

    if not questions:
        raise InterviewSessionError(
            "At least one interview question is required."
        )

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

    if candidate is None:
        raise InterviewSessionError(
            "Candidate not found."
        )

    job_description = (
        db.query(JobDescription)
        .filter(
            JobDescription.id
            == job_description_id
        )
        .first()
    )

    if job_description is None:
        raise InterviewSessionError(
            "Job description not found."
        )

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

    for index, question in enumerate(questions):

        db_question = InterviewQuestion(
            interview_id=interview.id,

            question_id=
                question["id"],

            question_order=
                index,

            question=
                question["question"],

            section=
                question.get(
                    "section",
                    "General",
                ),

            difficulty=
                question.get(
                    "difficulty",
                    "Medium",
                ),

            question_type=
                question.get(
                    "question_type",
                    "main",
                ),

            parent_question_id=
                question.get(
                    "parent_question_id"
                ),

            expected_topics=
                json.dumps(
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


# =========================================================
# GET SESSION
# =========================================================

def get_session(
    db: Session,
    session_id: str,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    return _session_to_schema(interview)


# =========================================================
# FINISH SESSION
# =========================================================

def finish_session(
    db: Session,
    session_id: str,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    # Already completed.
    if interview.status == "completed":
        return _session_to_schema(interview)

    # Manually finish the interview.
    # This allows the final report to be generated
    # even when the candidate answered only part
    # of the interview.
    interview.status = "completed"

    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)


# =========================================================
# GET CURRENT QUESTION
# =========================================================

def get_current_question(
    db: Session,
    session_id: str,
) -> dict | None:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
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


# =========================================================
# SUBMIT ANSWER
# =========================================================

def submit_answer(
    db: Session,
    session_id: str,
    answer: str,
) -> dict:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
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
        "message":
            "Answer submitted successfully.",
        "next_question":
            next_question,
    }


# =========================================================
# STORE EVALUATION
# =========================================================

def store_evaluation(
    db: Session,
    session_id: str,
    question_id: str,
    evaluation: dict,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
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
        evaluation.get(
            "strengths",
            [],
        )
    )

    db_answer.weaknesses = json.dumps(
        evaluation.get(
            "weaknesses",
            [],
        )
    )

    db_answer.feedback = evaluation.get(
        "feedback"
    )

    db_answer.missing_topics = json.dumps(
        evaluation.get(
            "missing_topics",
            [],
        )
    )

    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)


# =========================================================
# STORE ADAPTIVE DECISION
# =========================================================

def store_adaptive_decision(
    db: Session,
    session_id: str,
    question_id: str,
    decision: dict,
) -> InterviewSession:

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    adaptive_decision = AdaptiveDecision(
        interview_id=interview.id,

        question_id=
            question_id,

        action=
            decision["action"],

        reason=
            decision["reason"],

        next_difficulty=
            decision["next_difficulty"],

        focus_topic=
            decision.get("focus_topic"),

        follow_up_question=
            decision.get(
                "follow_up_question"
            ),
    )

    db.add(adaptive_decision)

    db.commit()
    db.refresh(interview)

    return _session_to_schema(interview)


# =========================================================
# ADD FOLLOW-UP QUESTION
# =========================================================

def add_follow_up_question(
    db: Session,
    session_id: str,
    question: str,
    parent_question_id: str,
    difficulty: str = "Medium",
    focus_topic: str | None = None,
):
    """
    Add a follow-up question directly to the database.

    Follow-up IDs remain short and flat:

        q2
        q2-F1
        q2-F2
        q2-F3

    This prevents IDs such as:

        q2-F1-F2-F3-F4

    from growing indefinitely.
    """

    interview = (
        db.query(Interview)
        .filter(
            Interview.session_id
            == session_id
        )
        .first()
    )

    if interview is None:
        raise InterviewSessionError(
            "Interview session not found."
        )

    # --------------------------------------------------
    # Determine the root/main question ID
    # --------------------------------------------------

    if "-F" in parent_question_id:
        root_question_id = (
            parent_question_id.split(
                "-F",
                1,
            )[0]
        )
    else:
        root_question_id = parent_question_id

    # --------------------------------------------------
    # Generate unique follow-up ID
    # --------------------------------------------------

    existing_questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id
        )
        .all()
    )

    existing_ids = {
        item.question_id
        for item in existing_questions
    }

    follow_up_number = 1

    while True:

        follow_up_id = (
            f"{root_question_id}-F"
            f"{follow_up_number}"
        )

        if follow_up_id not in existing_ids:
            break

        follow_up_number += 1

    # --------------------------------------------------
    # Find section
    # --------------------------------------------------

    parent_question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id,

            InterviewQuestion.question_id
            == parent_question_id,
        )
        .first()
    )

    if parent_question is None:

        # If parent is itself a follow-up,
        # search using the root question.
        parent_question = (
            db.query(InterviewQuestion)
            .filter(
                InterviewQuestion.interview_id
                == interview.id,

                InterviewQuestion.question_id
                == root_question_id,
            )
            .first()
        )

    section = (
        parent_question.section
        if parent_question
        else "General"
    )

    # --------------------------------------------------
    # Insert at current question position
    # --------------------------------------------------

    insert_position = (
        interview.current_question_index
    )

    # Shift existing questions forward.
    for existing_question in existing_questions:

        if (
            existing_question.question_order
            >= insert_position
        ):

            existing_question.question_order += 1

    # --------------------------------------------------
    # Create follow-up question
    # --------------------------------------------------

    follow_up = InterviewQuestion(
        interview_id=interview.id,

        question_id=follow_up_id,

        question_order=insert_position,

        question=question,

        section=section,

        difficulty=difficulty,

        question_type="follow_up",

        parent_question_id=parent_question_id,

        expected_topics=json.dumps(
            [focus_topic]
            if focus_topic
            else []
        ),
    )

    db.add(follow_up)

    # A follow-up means the interview continues.
    interview.status = "active"

    db.commit()
    db.refresh(interview)

    return _question_to_dict(follow_up)