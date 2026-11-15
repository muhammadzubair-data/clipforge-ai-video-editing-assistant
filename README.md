# ClipForge AI — Video Editing Assistant

A **working, local-first video editing application** that supports precise clip extraction, silence detection/removal, optional offline AI transcription, and vertical social video export. Built with Python, FFmpeg, and Streamlit.

> This is an MVP, not a fully automated viral-highlights finder. It does not rank highlights or burn captions into videos. Those are documented future enhancements.

## Features
- Upload MP4/MOV/MKV/WebM and preview it.
- Inspect duration and streams using FFprobe.
- Cut any time range and export MP4.
- Detect silences using FFmpeg `silencedetect` and export a concatenated non-silent cut.
- Optional 9:16 vertical export (1080×1920 letterboxed, no automatic face tracking).
- Optional local SRT generation using faster-whisper (CPU supported).
- Download edited MP4 and SRT.
- Automated unit tests and GitHub Actions CI.

## Installation (Windows PowerShell)
1. Install **Python 3.11+** and **FFmpeg**; verify `ffmpeg -version` and `ffprobe -version` work.
2. In the project directory:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`.

For optional AI subtitles: `pip install faster-whisper`. First model run downloads model weights. Offline use is possible after caching weights.

## Run a demo without your own footage
Generate a sample clip with FFmpeg (works without any media assets):

```bash
python scripts/create_demo.py
```

Upload `demo_video.mp4` to the app. The generated clip contains color bars and a synthetic tone separated by a quiet section. No third-party copyrighted assets are bundled.

## Testing
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Architecture
`app.py` is the Streamlit UI. `clipforge/core.py` handles FFmpeg commands, time ranges, silence detection, SRT serialization, and export. `clipforge/transcription.py` is an optional faster-whisper integration. `tests/` covers deterministic core logic. See `docs/ARCHITECTURE.md`.

## Limitations
- FFmpeg and FFprobe must be installed separately and available on PATH.
- CPU-based Whisper transcription may be slow; it is optional and not installed by default.
- Audio-less files do not support silence analysis. Some codecs or broken uploads may fail.
- Silence removal may produce awkward cuts; review exports before publishing.
- The app stores temporary uploads on the machine running Streamlit; no automatic cleanup beyond OS temporary storage. Do not deploy publicly with sensitive videos without authentication, retention limits, file size limits, and resource quotas.
- Video editing is compute-intensive; Streamlit Community Cloud resource limits may prevent large-video processing. Local use is recommended.
- ClipForge does not automatically discover viral highlights, detect faces, or burn captions into video in this MVP.

## License
MIT. See LICENSE.
