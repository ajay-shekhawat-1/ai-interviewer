import json

from groq import Groq

from app.llm.groq_client import (
    get_groq_client,
    get_groq_model,
)
from app.schemas.candidate import CandidateProfile
from app.schemas.interview import InterviewBlueprint
from app.schemas.jd import JDProfile


class InterviewBlueprintError(Exception):
    """
    Raised when interview blueprint generation fails.
    """


SYSTEM_PROMPT = """
You are an expert technical interviewer and interview architect.

Your task is to create a structured interview blueprint using:

1. The job description profile.
2. The candidate profile.

The blueprint must create a fair, role-relevant and
candidate-aware technical interview.

Return valid JSON with exactly these fields:

{
  "interview_type": "string",
  "difficulty": "string",
  "total_questions": 10,
  "sections": [
    {
      "name": "string",
      "question_count": 2,
      "difficulty": "string",
      "focus_areas": ["string"]
    }
  ],
  "candidate_focus_areas": ["string"],
  "rationale": "string"
}

Rules:

1. The interview must be based on the job requirements.
2. Do not invent skills that are unrelated to the job.
3. Use the candidate profile to personalize the interview.
4. Give more attention to important required skills.
5. Include candidate-specific focus areas when appropriate.
6. Skill gaps can be tested, but do not assume the candidate is
   incompetent simply because a skill is absent from the resume.
7. Projects and experience can be used for verification questions.
8. Keep the interview balanced.
9. Total question count must equal the sum of question_count
   across all sections.
10. Use between 5 and 20 total questions.
11. The value of total_questions MUST exactly equal the sum
    of question_count across all sections.

12. Do not create duplicate sections.

13. Prefer 3 to 6 sections for a normal interview.

14. Prioritize required skills over preferred skills.

15. Use projects and experience for candidate-specific questions
    when they are relevant to the target role.
16. Keep section names concise.
17. Return JSON only.

"""


def generate_interview_blueprint(
    jd_profile: JDProfile,
    candidate_profile: CandidateProfile,
) -> InterviewBlueprint:
    """
    Generate an interview blueprint from a JD profile
    and candidate profile.
    """

    client: Groq = get_groq_client()
    model = get_groq_model()

    user_prompt = f"""
JOB DESCRIPTION PROFILE:

{json.dumps(
    jd_profile.model_dump(),
    indent=2,
    ensure_ascii=False,
)}


CANDIDATE PROFILE:

{json.dumps(
    candidate_profile.model_dump(),
    indent=2,
    ensure_ascii=False,
)}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
            max_tokens=3000,
            response_format={
                "type": "json_object",
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise InterviewBlueprintError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        return InterviewBlueprint.model_validate(data)

    except json.JSONDecodeError as exc:
        raise InterviewBlueprintError(
            "Groq returned invalid JSON."
        ) from exc

    except InterviewBlueprintError:
        raise

    except Exception as exc:
        raise InterviewBlueprintError(
            "Unable to generate interview blueprint."
        ) from exc