from sqlalchemy.orm import Session

from app.services.answer_evaluator import (
    AnswerEvaluationError,
    evaluate_answer,
)

from app.services.adaptive_engine import (
    decide_next_action,
    generate_follow_up_question,
)

from app.services.interview_session import (
    add_follow_up_question,
    get_session,
    store_adaptive_decision,
    store_evaluation,
    submit_answer,
)


class InterviewLoopError(Exception):
    pass


def process_answer(
    db: Session,
    session_id: str,
    answer: str,
) -> dict:

    # ---------------------------------------------------------
    # 1. Get current interview session
    # ---------------------------------------------------------

    session = get_session(
        db=db,
        session_id=session_id,
    )

    if session.status == "completed":
        raise InterviewLoopError(
            "Interview has already been completed."
        )

    if (
        session.current_question_index
        >= len(session.questions)
    ):
        raise InterviewLoopError(
            "No question is currently available."
        )

    # ---------------------------------------------------------
    # 2. Get current question
    # ---------------------------------------------------------

    current_question = session.questions[
        session.current_question_index
    ]

    # ---------------------------------------------------------
    # 3. Evaluate answer
    #
    # Empty answer is allowed.
    # Irrelevant answer is allowed.
    # Both will receive low marks.
    # ---------------------------------------------------------

    try:

        evaluation = evaluate_answer(
            question=current_question,
            answer=answer,
        )

    except AnswerEvaluationError as exc:

        raise InterviewLoopError(
            str(exc)
        ) from exc

    # ---------------------------------------------------------
    # 4. Save the answer
    #
    # IMPORTANT:
    # This moves the interview to the next question.
    # We do this even for empty/irrelevant answers.
    # ---------------------------------------------------------

    submit_answer(
        db=db,
        session_id=session_id,
        answer=answer if answer.strip() else "[No answer provided]",
    )

    # ---------------------------------------------------------
    # 5. Save evaluation
    # ---------------------------------------------------------

    updated_session = store_evaluation(
        db=db,
        session_id=session_id,
        question_id=current_question["id"],
        evaluation=evaluation.model_dump(),
    )

    # ---------------------------------------------------------
    # 6. Calculate remaining questions
    # ---------------------------------------------------------

    remaining_questions = (
        len(updated_session.questions)
        - updated_session.current_question_index
    )

    # ---------------------------------------------------------
    # 7. Adaptive engine
    # ---------------------------------------------------------

    decision = decide_next_action(
        evaluation=evaluation,
        remaining_questions=remaining_questions,
        current_difficulty=current_question.get(
            "difficulty",
            "Medium",
        ),
    )

    # ---------------------------------------------------------
    # 8. Generate follow-up if adaptive engine requires it
    # ---------------------------------------------------------

    follow_up_question = None

    if (
        decision.action == "follow_up"
        and decision.focus_topic
    ):

        follow_up_question = generate_follow_up_question(
            original_question=current_question,
            answer=answer,
            missing_topic=decision.focus_topic,
        )

        decision.follow_up_question = (
            follow_up_question
        )

        add_follow_up_question(
            db=db,
            session_id=session_id,
            question=follow_up_question,
            parent_question_id=current_question["id"],
            difficulty=decision.next_difficulty,
            focus_topic=decision.focus_topic,
        )

    # ---------------------------------------------------------
    # 9. Save adaptive decision
    # ---------------------------------------------------------

    store_adaptive_decision(
        db=db,
        session_id=session_id,
        question_id=current_question["id"],
        decision=decision.model_dump(),
    )

    # ---------------------------------------------------------
    # 10. Get latest session
    # ---------------------------------------------------------

    final_session = get_session(
        db=db,
        session_id=session_id,
    )

    # ---------------------------------------------------------
    # 11. Get next question
    # ---------------------------------------------------------

    next_question = None

    if (
        final_session.current_question_index
        < len(final_session.questions)
    ):

        next_question = final_session.questions[
            final_session.current_question_index
        ]

    # ---------------------------------------------------------
    # 12. Return result
    # ---------------------------------------------------------

    return {
        "status": "success",

        "message": (
            "Answer evaluated successfully."
        ),

        "retry": False,

        "session": final_session,

        "evaluation": evaluation,

        "decision": decision,

        "next_question": next_question,
    }