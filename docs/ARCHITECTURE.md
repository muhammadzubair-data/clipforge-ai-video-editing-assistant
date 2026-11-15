# Architecture and future roadmap

User video → Streamlit uploader → temporary local file → FFprobe metadata → FFmpeg edit/silence processing → downloadable MP4. Optional faster-whisper produces SRT text.

The application does not call a paid API. Video files remain on the host machine running the app. This is not the same as end-to-end privacy on a remotely hosted server.

## Future enhancements (not implemented)
- Scene boundary detection and transcript-aware highlight suggestions.
- Subtitle burn-in and styled captions.
- Automatic reframing based on subject tracking.
- Multi-clip editing timeline, B-roll, and batch exports.
- User accounts, queued jobs, and durable object storage.
- Evaluation dataset for highlight quality and transcript word error rate.
