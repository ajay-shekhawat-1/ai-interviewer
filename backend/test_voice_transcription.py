from pathlib import Path

from app.services.voice_transcription import transcribe_audio


audio_path = Path("test_audio.mp3")

if not audio_path.exists():
    print("ERROR: test_audio.mp3 not found.")
    raise SystemExit(1)

audio_bytes = audio_path.read_bytes()

text = transcribe_audio(
    file_bytes=audio_bytes,
    filename=audio_path.name,
)

print("\n--- TRANSCRIPTION ---")
print(text)
print("---------------------")