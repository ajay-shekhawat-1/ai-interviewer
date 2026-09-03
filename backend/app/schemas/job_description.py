from pydantic import BaseModel, Field


class CreateJobDescriptionRequest(BaseModel):
    title: str = Field(
        default="Job Position",
        min_length=1,
        max_length=200,
    )

    raw_text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    raw_text: str
    job_title: str | None = None
    experience_level: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    technical_topics: list[str] = Field(default_factory=list)