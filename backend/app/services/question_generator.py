import json

from app.llm.groq_client import get_groq_client, get_groq_model
from app.schemas.question import QuestionSet


class QuestionGenerationError(Exception):
    """
    Raised when interview question generation fails.
    """

    pass


def generate_questions(
    jd_profile: dict,
    candidate_profile: dict,
    interview_blueprint: dict,
) -> QuestionSet:

    client = get_groq_client()
    model = get_groq_model()

    system_prompt = """
You are an expert technical interviewer.

Your task is to generate interview questions using:

1. The job description profile.
2. The candidate profile.
3. The interview blueprint.

Generate questions that are:

- Relevant to the target job.
- Appropriate for the candidate's experience.
- Consistent with the interview blueprint.
- Technically meaningful.
- Non-duplicate.
- Suitable for a real interview.

Return valid JSON with exactly this structure:

{
  "questions": [
    {
      "id": "q1",
      "section": "string",
      "question": "string",
      "difficulty": "string",
      "expected_topics": ["string"]
    }
  ]
}

Rules:

1. Follow the interview blueprint exactly.
2. Generate exactly the number of questions specified by
   the blueprint's total_questions.
3. The number of generated questions must equal total_questions.
4. Use the blueprint sections when creating questions.
5. Prioritize required job skills.
6. Use candidate projects and experience for personalized questions.
7. Do not invent candidate experience.
8. Do not ask unrelated questions.
9. Avoid duplicate or nearly identical questions.
10. Mix conceptual, practical, and candidate-specific questions
    when appropriate.
11. Difficulty should match the blueprint.
12. expected_topics should contain important concepts that a
    strong answer should cover.
13. Return JSON only.
"""

    user_prompt = f"""
JOB DESCRIPTION PROFILE:

{json.dumps(
    jd_profile,
    indent=2,
    ensure_ascii=False
)}


CANDIDATE PROFILE:

{json.dumps(
    candidate_profile,
    indent=2,
    ensure_ascii=False
)}


INTERVIEW BLUEPRINT:

{json.dumps(
    interview_blueprint,
    indent=2,
    ensure_ascii=False
)}


Generate the complete interview question set.
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
            max_tokens=5000,
            response_format={
                "type": "json_object"
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise QuestionGenerationError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        question_set = QuestionSet.model_validate(data)

        expected_count = interview_blueprint["total_questions"]

        actual_count = len(question_set.questions)

        if actual_count != expected_count:
            raise QuestionGenerationError(
                f"Expected {expected_count} questions, "
                f"but generated {actual_count}."
            )

        return question_set

    except QuestionGenerationError:
        raise

    except Exception as exc:
        raise QuestionGenerationError(
            f"Question generation failed: {exc}"
        ) from exc