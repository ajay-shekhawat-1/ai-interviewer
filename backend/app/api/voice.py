from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.voice import TranscriptionResponse
from app.services.voice_transcription import (
    VoiceTranscriptionError,
    transcribe_audio,
)

router = APIRouter(
    prefix="/api/voice",
    tags=["Voice"],
)


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def transcribe_voice(
    file: UploadFile = File(...),
) -> TranscriptionResponse:

    try:
        file_bytes = await file.read()

        text = transcribe_audio(
            file_bytes=file_bytes,
            filename=file.filename or "",
        )

        return TranscriptionResponse(
            text=text,
        )

    except VoiceTranscriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc