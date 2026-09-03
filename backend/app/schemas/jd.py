from pydantic import BaseModel, Field


class JDAnalyzeRequest(BaseModel):
    """
    Request payload for job description analysis.
    """

    job_description: str = Field(
        ...,
        min_length=50,
        max_length=30000,
        description="Raw job description text.",
    )


class JDProfile(BaseModel):
    """
    Structured representation of a job description.
    """

    job_title: str = Field(
        ...,
        description="Primary job title.",
    )

    experience_level: str = Field(
        ...,
        description="Expected experience level.",
    )

    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills explicitly required for the role.",
    )

    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Skills that are preferred but not mandatory.",
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key responsibilities of the role.",
    )

    technical_topics: list[str] = Field(
        default_factory=list,
        description="Technical areas that should be assessed during interview.",
    )


class CreateJDRequest(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=50,
        max_length=30000,
        description="Raw job description text.",
    )


class JDResponse(BaseModel):
    job_description_id: int
    profile: JDProfile