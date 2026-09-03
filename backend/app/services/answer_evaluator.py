import json

from app.llm.groq_client import (
    get_groq_client,
    get_groq_model,
)

from app.schemas.evaluation import AnswerEvaluation


class AnswerEvaluationError(Exception):
    pass


def evaluate_answer(
    question: dict,
    answer: str,
) -> AnswerEvaluation:

    client = get_groq_client()
    model = get_groq_model()

    system_prompt = """
You are an expert technical interviewer and candidate evaluator.

Evaluate the candidate's answer against the interview question.

Return valid JSON with exactly these fields:

{
  "question_id": "string",
  "technical_score": 0,
  "relevance_score": 0,
  "completeness_score": 0,
  "communication_score": 0,
  "overall_score": 0,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "feedback": "string",
  "missing_topics": ["string"]
}

SCORING RULES:

technical_score:
How technically correct is the answer?

relevance_score:
How directly does the answer address the question?

completeness_score:
How completely does the answer cover the expected topics?

communication_score:
How clearly and logically is the answer explained?

overall_score:
Overall quality of the answer.

IMPORTANT RULES:

1. Scores must be between 0 and 10.

2. If the candidate gives an empty answer:
   - technical_score = 0
   - relevance_score = 0
   - completeness_score = 0
   - communication_score = 0
   - overall_score = 0
   - strengths should be empty
   - weaknesses should explain that no answer was provided
   - feedback should explain that the candidate did not provide an answer
   - missing_topics should contain the important expected topics

3. If the candidate gives an irrelevant answer:
   - Give very low relevance marks.
   - Reduce the overall score.
   - Reduce technical and completeness scores when appropriate.
   - Do NOT treat the answer as correct.
   - Clearly explain that the answer did not address the question.

4. If the candidate gives a relevant answer:
   - Evaluate it normally.
   - Do not reduce marks just because the answer is short.
   - A concise but correct answer can receive a high score.

5. If the candidate says "I don't know":
   - Treat it as an actual answer.
   - Give low scores.
   - Do not treat it as empty.

6. Do not give high marks simply because the answer is long.

7. Do not invent facts about the candidate.

8. Use expected_topics to judge completeness.

9. Identify important missing concepts in missing_topics.

10. Return JSON only.
"""

    user_prompt = f"""
INTERVIEW QUESTION:

{json.dumps(
    question,
    indent=2,
    ensure_ascii=False,
)}

CANDIDATE ANSWER:

{answer if answer.strip() else "[NO ANSWER PROVIDED]"}

Evaluate the candidate's answer.

If the answer is empty or unrelated, give appropriately low
scores. Do not ask the candidate to repeat the question.
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
            temperature=0,
            max_tokens=2500,
            response_format={
                "type": "json_object",
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise AnswerEvaluationError(
                "Groq returned an empty evaluation."
            )

        data = json.loads(content)

        evaluation = AnswerEvaluation.model_validate(data)

        if evaluation.question_id != question["id"]:
            raise AnswerEvaluationError(
                "Evaluation question_id does not match "
                "the original question."
            )

        return evaluation

    except AnswerEvaluationError:
        raise

    except Exception as exc:
        raise AnswerEvaluationError(
            f"Answer evaluation failed: {exc}"
        ) from exc