from pathlib import Path

from app.llm.groq_client import get_groq_client


class VoiceTranscriptionError(Exception):
    pass


WHISPER_MODEL = "whisper-large-v3-turbo"


def transcribe_audio(
    file_bytes: bytes,
    filename: str,
) -> str:
    if not file_bytes:
        raise VoiceTranscriptionError("Audio file is empty.")

    if not filename:
        raise VoiceTranscriptionError("Audio filename is required.")

    file_extension = Path(filename).suffix.lower()

    allowed_extensions = {
        ".mp3",
        ".wav",
        ".m4a",
        ".webm",
        ".mp4",
    }

    if file_extension not in allowed_extensions:
        raise VoiceTranscriptionError(
            "Unsupported audio format. "
            "Supported formats: MP3, WAV, M4A, WEBM, MP4."
        )

    try:
        client = get_groq_client()

        transcription = client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model=WHISPER_MODEL,
            response_format="text",
        )

        text = str(transcription).strip()

        if not text:
            raise VoiceTranscriptionError(
                "Whisper returned an empty transcription."
            )

        return text

    except VoiceTranscriptionError:
        raise

    except Exception as exc:
        raise VoiceTranscriptionError(
            f"Audio transcription failed: {str(exc)}"
        ) from exc