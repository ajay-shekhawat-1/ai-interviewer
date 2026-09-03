from pydantic import BaseModel, Field, field_validator


class QuestionGenerationRequest(BaseModel):
    """
    Input required to generate interview questions.
    """

    jd_profile: dict = Field(
        ...,
        description="Structured job description profile.",
    )

    candidate_profile: dict = Field(
        ...,
        description="Structured candidate profile.",
    )

    interview_blueprint: dict = Field(
        ...,
        description="Structured interview blueprint.",
    )


class InterviewQuestion(BaseModel):
    """
    Represents one generated interview question.
    """

    id: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )

    section: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    question: str = Field(
        ...,
        min_length=10,
        max_length=1000,
    )

    difficulty: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    expected_topics: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator("id", "section", "question", "difficulty")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()


class QuestionSet(BaseModel):
    """
    Complete set of generated interview questions.
    """

    questions: list[InterviewQuestion] = Field(
        ...,
        min_length=1,
        max_length=20,
    )