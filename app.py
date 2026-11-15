import json
import tempfile
from pathlib import Path
import streamlit as st
from clipforge.core import duration, find_silences, keep_intervals, export_segment, concat_segments, probe
from clipforge.transcription import transcribe_local

st.set_page_config(page_title='ClipForge AI',page_icon='🎬',layout='wide')
st.title('🎬 ClipForge AI')
st.caption('Local-first video editing assistant · FFmpeg-powered · optional AI captions')
st.info('Uploads are processed in a temporary directory on the server running this app. Use local deployment for private footage.')
file=st.file_uploader('Upload a video',type=['mp4','mov','mkv','webm'])
if not file:
    st.markdown('**Workflow:** Upload → inspect → select clip or remove silence → export → optional subtitles. No API key required for core editing.')
    st.stop()
if st.session_state.get('upload_id') != (file.name,file.size):
    st.session_state.upload_id=(file.name,file.size)
    st.session_state.workspace=tempfile.mkdtemp(prefix='clipforge_')
    target=Path(st.session_state.workspace)/('source'+Path(file.name).suffix.lower())
    target.write_bytes(file.getbuffer())
    st.session_state.source=str(target)
    st.session_state.pop('output',None)
src=Path(st.session_state.source);work=Path(st.session_state.workspace)
try:
    meta=probe(src);length=duration(src)
except Exception as exc:
    st.error(f'Cannot inspect video: {exc}');st.stop()
st.video(str(src))
c1,c2,c3=st.columns(3)
c1.metric('Duration',f'{length:.1f}s');c2.metric('Size',f'{src.stat().st_size/1024/1024:.1f} MB');c3.metric('Streams',len(meta.get('streams',[])))
vertical=st.checkbox('Export 9:16 vertical video (letterbox to preserve image)',value=True)
tab1,tab2,tab3=st.tabs(['✂️ Clip editor','🔇 Silence removal','📝 AI subtitles (optional)'])
with tab1:
    start=st.number_input('Start (seconds)',min_value=0.0,max_value=max(0.0,length-0.1),value=0.0,step=1.0)
    end=st.number_input('End (seconds)',min_value=0.1,max_value=length,value=min(length,start+30),step=1.0)
    if st.button('Export selected clip',type='primary'):
        try:
            out=work/'selected_clip.mp4';export_segment(src,out,start,end,vertical)
            st.session_state.output=str(out);st.success('Clip exported')
        except Exception as exc:st.error(str(exc))
with tab2:
    threshold=st.slider('Silence threshold (dB)',-60,-15,-35)
    minimum=st.slider('Minimum silence length (seconds)',0.2,2.0,0.55,0.05)
    if st.button('Analyze silence'):
        try:
            spans=find_silences(src,threshold,minimum)
            st.session_state.silences=spans
            st.write(f'Found {len(spans)} silent intervals')
            st.dataframe([{'start':round(a,2),'end':round(b,2)} for a,b in spans])
        except Exception as exc:st.error(str(exc))
    if st.button('Remove silence and export'):
        try:
            spans=find_silences(src,threshold,minimum)
            intervals=keep_intervals(length,spans)
            out=work/'silence_removed.mp4';concat_segments(src,out,intervals,work/'parts',vertical)
            st.session_state.output=str(out);st.success(f'Exported {len(intervals)} retained segments')
        except Exception as exc:st.error(str(exc))
with tab3:
    st.write('Optional offline speech-to-text with faster-whisper. First run downloads a model; internet is needed for that initial download.')
    model=st.selectbox('Model', ['tiny','base','small'])
    if st.button('Generate SRT subtitles'):
        try:
            srt,language=transcribe_local(src,work/'captions.srt',model)
            st.success(f'Subtitles generated; detected language: {language}')
            st.download_button('Download subtitles (.srt)',Path(srt).read_bytes(),'captions.srt','text/plain')
        except Exception as exc:st.error(str(exc))
    if (work/'captions.srt').exists():
        st.download_button('Download existing SRT', (work/'captions.srt').read_bytes(),'captions.srt')
if st.session_state.get('output') and Path(st.session_state.output).exists():
    out=Path(st.session_state.output)
    st.subheader('Export preview')
    st.video(str(out))
    st.download_button('⬇️ Download edited MP4',out.read_bytes(),out.name,'video/mp4')
