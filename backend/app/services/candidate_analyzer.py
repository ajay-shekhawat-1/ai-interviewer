import json

from groq import Groq

from app.llm.groq_client import (
    get_groq_client,
    get_groq_model,
)
from app.schemas.candidate import CandidateProfile


class CandidateAnalysisError(Exception):
    """
    Raised when candidate analysis fails.
    """


SYSTEM_PROMPT = """
You are an expert technical recruiter and candidate-profile analyst.

Analyze the candidate's resume against the provided job description.

Return a JSON object with exactly these fields:

{
  "candidate_name": "string",
  "education": ["string"],
  "skills": ["string"],
  "experience": ["string"],
  "projects": ["string"],
  "matched_skills": ["string"],
  "skill_gaps": ["string"],
  "experience_summary": "string"
}

Rules:

1. Use only information supported by the resume and job description.
2. Never invent candidate experience, skills, education, or projects.
3. "skills" should contain skills demonstrated in the resume.
4. "matched_skills" should contain skills required by the job description
   that are also supported by the resume.
5. "skill_gaps" should contain important job requirements that are not
   demonstrated in the resume.
6. Do not treat a skill as matched merely because it is mentioned in the
   job description.
7. Keep lists concise and remove duplicates.
8. Focus on information relevant to the target role.
9. Return valid JSON only.
"""


def analyze_candidate(
    resume_text: str,
    job_description: str,
) -> CandidateProfile:
    """
    Analyze a candidate resume against a job description.
    """

    client: Groq = get_groq_client()
    model = get_groq_model()

    user_prompt = f"""
Candidate Resume:

{resume_text}


Job Description:

{job_description}
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
            max_tokens=2500,
            response_format={
                "type": "json_object",
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise CandidateAnalysisError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        return CandidateProfile.model_validate(data)

    except json.JSONDecodeError as exc:
        raise CandidateAnalysisError(
            "Groq returned invalid JSON."
        ) from exc

    except CandidateAnalysisError:
        raise

    except Exception as exc:
        raise CandidateAnalysisError(
            f"Unable to analyze the candidate: {type(exc).__name__}: {str(exc)}"
        ) from exc