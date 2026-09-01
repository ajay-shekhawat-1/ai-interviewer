from pydantic import BaseModel, Field


class CandidateAnalyzeRequest(BaseModel):
    """
    Request payload for candidate analysis.
    """

    resume_text: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Extracted and normalized resume text.",
    )

    job_description: str = Field(
        ...,
        min_length=50,
        max_length=30000,
        description="Raw job description text.",
    )


class CandidateProfile(BaseModel):
    """
    Structured representation of a candidate
    relative to a specific job description.
    """

    candidate_name: str = Field(
        default="Unknown",
        description="Candidate's name if available.",
    )

    education: list[str] = Field(
        default_factory=list,
        description="Candidate education details.",
    )

    skills: list[str] = Field(
        default_factory=list,
        description="Skills explicitly found in the resume.",
    )

    experience: list[str] = Field(
        default_factory=list,
        description="Relevant work experience.",
    )

    projects: list[str] = Field(
        default_factory=list,
        description="Relevant projects from the resume.",
    )

    matched_skills: list[str] = Field(
        default_factory=list,
        description="Job-required skills found in the candidate profile.",
    )

    skill_gaps: list[str] = Field(
        default_factory=list,
        description="Important job requirements not demonstrated by the resume.",
    )

    experience_summary: str = Field(
        default="",
        description="Short summary of the candidate's relevant experience.",
    )