from pydantic import BaseModel, Field
from typing import Literal


# ---------------------------------------------------------
# Create Session Request
# ---------------------------------------------------------

class CreateInterviewSessionRequest(BaseModel):
    candidate_id: int = Field(
        ...,
        ge=1,
        description="Existing candidate ID.",
    )

    job_description_id: int = Field(
        ...,
        ge=1,
        description="Existing job description ID.",
    )

    questions: list[dict] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Generated interview questions.",
    )


# ---------------------------------------------------------
# Submit Answer Request
# ---------------------------------------------------------

class SubmitAnswerRequest(BaseModel):
    answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


# ---------------------------------------------------------
# Interview Answer
# ---------------------------------------------------------

class InterviewAnswer(BaseModel):
    question_id: str
    question: str
    answer: str
    evaluation: dict | None = None


# ---------------------------------------------------------
# Adaptive History
# ---------------------------------------------------------

class AdaptiveHistory(BaseModel):
    question_id: str

    action: str

    reason: str

    next_difficulty: str

    focus_topic: str | None = None

    follow_up_question: str | None = None


# ---------------------------------------------------------
# Interview Question
# ---------------------------------------------------------

class SessionQuestion(BaseModel):
    id: str

    section: str

    question: str

    difficulty: str

    expected_topics: list[str] = Field(
        default_factory=list
    )

    question_type: Literal[
        "main",
        "follow_up",
    ] = "main"

    parent_question_id: str | None = None


# ---------------------------------------------------------
# Interview Session
# ---------------------------------------------------------

class InterviewSession(BaseModel):
    session_id: str

    candidate_name: str

    questions: list[dict]

    current_question_index: int = Field(
        default=0,
        ge=0,
    )

    answers: list[InterviewAnswer] = Field(
        default_factory=list,
    )

    adaptive_history: list[AdaptiveHistory] = Field(
        default_factory=list,
    )

    status: str = Field(
        default="active",
    )