from .core import write_srt


def transcribe_local(video, output_srt, model_name='tiny', language=None):
    """Optional local Whisper transcription. Install faster-whisper separately."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError('Install optional transcription dependency: pip install faster-whisper') from exc
    model=WhisperModel(model_name, device='cpu', compute_type='int8')
    segments, info=model.transcribe(str(video),language=language, vad_filter=True)
    chunks=[(s.start,s.end,s.text) for s in segments]
    if not chunks:
        raise RuntimeError('No speech was detected')
    return write_srt(chunks,output_srt), info.language
