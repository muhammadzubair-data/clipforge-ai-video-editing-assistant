import json
import re
import shutil
import subprocess
from pathlib import Path


def require_ffmpeg():
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('FFmpeg and FFprobe are required on PATH. See README.')


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr[-2500:] or 'FFmpeg failed')
    return result.stdout


def probe(path):
    require_ffmpeg()
    return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))


def duration(path):
    return float(probe(path)['format']['duration'])


def find_silences(path, threshold=-35, minimum=0.55):
    require_ffmpeg()
    cmd=['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af',f'silencedetect=noise={threshold}dB:d={minimum}','-f','null','-']
    proc=subprocess.run(cmd,capture_output=True,text=True)
    if proc.returncode and 'silence_start' not in proc.stderr:
        raise RuntimeError(proc.stderr[-1200:])
    starts=[]; spans=[]
    for line in proc.stderr.splitlines():
        a=re.search(r'silence_start:\s*([\d.]+)',line)
        b=re.search(r'silence_end:\s*([\d.]+)',line)
        if a: starts.append(float(a.group(1)))
        if b and starts: spans.append((starts.pop(0),float(b.group(1))))
    if starts: spans.append((starts[0],duration(path)))
    return spans


def keep_intervals(total, silences, padding=0.12, min_clip=0.35):
    silences=sorted((max(0,a+padding),min(total,b-padding)) for a,b in silences if b-a>2*padding)
    keep=[];cursor=0.0
    for a,b in silences:
        a=max(cursor,a)
        if a-cursor>=min_clip:keep.append((cursor,a))
        cursor=max(cursor,b)
    if total-cursor>=min_clip:keep.append((cursor,total))
    return keep


def export_segment(src,dest,start,end,vertical=False):
    require_ffmpeg()
    if end<=start:raise ValueError('End must be greater than start')
    vf='scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1' if vertical else 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-ss',str(start),'-i',str(src),'-t',str(end-start),'-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-movflags','+faststart',str(dest)])
    return dest


def concat_segments(src,dest,intervals,workdir,vertical=False):
    if not intervals:raise ValueError('No non-silent footage to export')
    workdir=Path(workdir);workdir.mkdir(parents=True,exist_ok=True)
    parts=[]
    for i,(a,b) in enumerate(intervals):
        part=workdir/f'part_{i:03}.mp4';export_segment(src,part,a,b,vertical);parts.append(part)
    listing=workdir/'concat.txt'
    listing.write_text(''.join("file '"+p.resolve().as_posix().replace("'", "'\\''")+"'\n" for p in parts))
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(dest)])
    return dest


def timestamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def write_srt(chunks,path):
    lines=[]
    for i,(start,end,content) in enumerate(chunks,1):
        lines.append(f'{i}\n{timestamp(start)} --> {timestamp(end)}\n{content.strip()}\n')
    Path(path).write_text('\n'.join(lines),encoding='utf-8')
    return path
