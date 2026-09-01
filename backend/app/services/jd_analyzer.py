import json

from groq import Groq

from app.llm.groq_client import get_groq_client, get_groq_model
from app.schemas.jd import JDProfile


class JDAnalysisError(Exception):
    """
    Raised when JD analysis fails.
    """


SYSTEM_PROMPT = """
You are an expert technical recruiter and job-description analyst.

Analyze the provided job description and extract only information
supported by the job description.

Return a JSON object with exactly these fields:

{
  "job_title": "string",
  "experience_level": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "responsibilities": ["string"],
  "technical_topics": ["string"]
}

Rules:

1. Do not invent skills or responsibilities.
2. Keep required_skills separate from preferred_skills.
3. technical_topics should contain areas that can reasonably be assessed
   in a technical interview.
4. Keep each list concise and avoid duplicates.
5. If a field cannot be determined, return a reasonable empty string
   or empty list.
6. Return valid JSON only.
"""


def analyze_job_description(
    job_description: str,
) -> JDProfile:
    """
    Analyze a raw job description using Groq.
    """

    client: Groq = get_groq_client()
    model = get_groq_model()

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
                    "content": (
                        "Analyze this job description:\n\n"
                        f"{job_description}"
                    ),
                },
            ],
            temperature=0,
            max_tokens=2000,
            response_format={
                "type": "json_object",
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise JDAnalysisError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        return JDProfile.model_validate(data)

    except json.JSONDecodeError as exc:
        raise JDAnalysisError(
            "Groq returned invalid JSON."
        ) from exc

    except Exception as exc:
        if isinstance(exc, JDAnalysisError):
            raise

        raise JDAnalysisError(
            "Unable to analyze the job description."
        ) from exc