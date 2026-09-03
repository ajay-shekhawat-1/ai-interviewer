from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Transcribed text from the uploaded audio.",
    )