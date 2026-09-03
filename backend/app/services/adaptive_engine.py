from app.schemas.adaptive import AdaptiveDecision
from app.schemas.evaluation import AnswerEvaluation


class AdaptiveInterviewError(Exception):
    """
    Raised when adaptive interview logic fails.
    """

    pass


def decide_next_action(
    evaluation: AnswerEvaluation,
    remaining_questions: int,
    current_difficulty: str,
) -> AdaptiveDecision:
    """
    Decide what the interviewer should do after evaluating
    the candidate's answer.
    """

    if remaining_questions <= 0:
        return AdaptiveDecision(
            action="complete",
            reason="No questions remain in the interview.",
            next_difficulty=current_difficulty,
            follow_up_question=None,
            focus_topic=None,
        )

    overall = evaluation.overall_score
    completeness = evaluation.completeness_score
    relevance = evaluation.relevance_score

    # Very poor answer or irrelevant answer.
    if relevance < 4 or overall < 4:

        return AdaptiveDecision(
            action="decrease_difficulty",
            reason=(
                "The candidate struggled with the current "
                "question. The next question should be easier "
                "to establish understanding."
            ),
            next_difficulty="Easy",
            follow_up_question=None,
            focus_topic=None,
        )

    # Strong answer but important concepts are missing.
    if (
        overall >= 6
        and completeness < 7
        and evaluation.missing_topics
    ):

        return AdaptiveDecision(
            action="follow_up",
            reason=(
                "The candidate demonstrated reasonable "
                "understanding but missed important concepts."
            ),
            next_difficulty=current_difficulty,
            follow_up_question=None,
            focus_topic=evaluation.missing_topics[0],
        )

    # Excellent answer.
    if overall >= 8:

        return AdaptiveDecision(
            action="increase_difficulty",
            reason=(
                "The candidate demonstrated strong "
                "understanding of the current topic."
            ),
            next_difficulty="Hard",
            follow_up_question=None,
            focus_topic=None,
        )

    # Normal answer.
    return AdaptiveDecision(
        action="continue",
        reason=(
            "The candidate demonstrated an acceptable "
            "level of understanding."
        ),
        next_difficulty=current_difficulty,
        follow_up_question=None,
        focus_topic=None,
    )
import json

from app.llm.groq_client import (
    get_groq_client,
    get_groq_model,
)


def generate_follow_up_question(
    original_question: dict,
    answer: str,
    missing_topic: str,
) -> str:

    client = get_groq_client()
    model = get_groq_model()

    system_prompt = """
You are an expert technical interviewer.

Generate exactly one concise follow-up interview question.

The follow-up must:

1. Be directly related to the original question.
2. Focus on the missing topic.
3. Not repeat the original question.
4. Be appropriate for the candidate's current level.
5. Test understanding rather than memorization.
6. Return JSON only.

Required format:

{
  "question": "string"
}
"""

    user_prompt = f"""
ORIGINAL QUESTION:

{json.dumps(
    original_question,
    indent=2,
    ensure_ascii=False,
)}


CANDIDATE ANSWER:

{answer}


MISSING TOPIC:

{missing_topic}


Generate one follow-up question.
"""

    try:

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.2,
            max_tokens=500,
            response_format={
                "type": "json_object"
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise AdaptiveInterviewError(
                "Groq returned an empty follow-up question."
            )

        data = json.loads(content)

        question = data.get("question")

        if not question:
            raise AdaptiveInterviewError(
                "Groq did not return a follow-up question."
            )

        return question.strip()

    except AdaptiveInterviewError:
        raise

    except Exception as exc:

        raise AdaptiveInterviewError(
            f"Follow-up question generation failed: {exc}"
        ) from exc