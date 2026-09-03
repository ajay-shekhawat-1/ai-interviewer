from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.candidate import CandidateProfile
from app.schemas.jd import JDProfile


class InterviewBlueprintRequest(BaseModel):
    """
    Input required to generate an interview blueprint.
    """

    jd_profile: JDProfile = Field(
        ...,
        description="Structured job description profile.",
    )

    candidate_profile: CandidateProfile = Field(
        ...,
        description="Structured candidate profile.",
    )


class InterviewSection(BaseModel):
    """
    Represents one section of the interview.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    question_count: int = Field(
        ...,
        ge=1,
        le=20,
    )

    difficulty: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    focus_areas: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("difficulty")
    @classmethod
    def normalize_difficulty(cls, value: str) -> str:
        return value.strip()


class InterviewBlueprint(BaseModel):
    """
    Structured interview strategy.
    """

    interview_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    difficulty: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    total_questions: int = Field(
        ...,
        ge=5,
        le=20,
    )

    sections: list[InterviewSection] = Field(
        ...,
        min_length=1,
        max_length=10,
    )

    candidate_focus_areas: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    rationale: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_question_count(self):
        """
        Ensure total_questions exactly matches
        the sum of all section question counts.
        """

        section_total = sum(
            section.question_count
            for section in self.sections
        )

        if section_total != self.total_questions:
            raise ValueError(
                "total_questions must equal the sum of "
                "section question_count values."
            )

        return self