from pydantic import BaseModel, Field

from app.schemas.interview import InterviewBlueprint
from app.schemas.session import InterviewSession


class StartInterviewRequest(BaseModel):
    candidate_id: int = Field(..., ge=1)
    job_description_id: int = Field(..., ge=1)


class StartInterviewResponse(BaseModel):
    session: InterviewSession
    blueprint: InterviewBlueprint