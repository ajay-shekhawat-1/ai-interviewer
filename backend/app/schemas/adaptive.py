from typing import Literal

from pydantic import BaseModel, Field


AdaptiveAction = Literal[
    "continue",
    "follow_up",
    "increase_difficulty",
    "decrease_difficulty",
    "complete",
]


class AdaptiveDecision(BaseModel):
    """
    Decision about what the interviewer should do next.
    """

    action: AdaptiveAction

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    next_difficulty: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    follow_up_question: str | None = Field(
        default=None,
        max_length=1000,
    )

    focus_topic: str | None = Field(
        default=None,
        max_length=200,
    )