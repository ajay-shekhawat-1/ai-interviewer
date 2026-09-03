from pydantic import BaseModel, Field, field_validator


class AnswerEvaluation(BaseModel):
    """
    Evaluation of one candidate answer.
    """

    question_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )

    technical_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    relevance_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    completeness_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    communication_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    overall_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    strengths: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    feedback: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    missing_topics: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator("question_id")
    @classmethod
    def strip_question_id(cls, value: str) -> str:
        return value.strip()


class InterviewReport(BaseModel):
    """
    Final report for a completed interview.
    """

    candidate_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    total_questions: int = Field(
        ...,
        ge=1,
    )

    answered_questions: int = Field(
        ...,
        ge=0,
    )

    technical_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    relevance_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    completeness_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    communication_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    overall_score: float = Field(
        ...,
        ge=0,
        le=10,
    )

    strengths: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    skill_gaps: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    recommendation: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    summary: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    question_results: list[dict] = Field(
        default_factory=list,
        max_length=50,
    )