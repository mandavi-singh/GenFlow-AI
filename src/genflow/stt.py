from faster_whisper import WhisperModel

_models: dict[str, WhisperModel] = {}


def get_model(size: str = "small") -> WhisperModel:
    if size not in _models:
        _models[size] = WhisperModel(size, device="cpu", compute_type="int8")
    return _models[size]


def transcribe(audio_bytes: bytes, language: str | None = None) -> dict:
    import tempfile
    from pathlib import Path

    model = get_model("small")
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp = Path(f.name)
    try:
        segments, info = model.transcribe(str(tmp), language=language)
        text = " ".join(s.text.strip() for s in segments).strip()
        return {"text": text, "language": info.language}
    finally:
        tmp.unlink(missing_ok=True)
