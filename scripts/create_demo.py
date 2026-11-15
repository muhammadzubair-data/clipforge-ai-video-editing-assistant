"""Generate a short synthetic video with an audible-quiet-audible sequence."""
import shutil
import subprocess
from pathlib import Path

if not shutil.which('ffmpeg'):
    raise SystemExit('FFmpeg is required. See README.')
root=Path(__file__).resolve().parents[1]
out=root/'demo_video.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','lavfi','-i','testsrc2=size=640x360:rate=24:duration=9','-f','lavfi','-i','sine=frequency=440:sample_rate=44100:duration=9','-filter_complex',"[1:a]volume='if(between(t,3,6),0,0.5)':eval=frame[a]",'-map','0:v','-map','[a]','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(out)]
subprocess.run(cmd,check=True)
print('Created',out)
