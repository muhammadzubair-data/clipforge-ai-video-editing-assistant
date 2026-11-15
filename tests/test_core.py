from pathlib import Path
import pytest
from clipforge.core import keep_intervals,timestamp,write_srt

def test_intervals():
    assert keep_intervals(10,[(2,4),(7,8)],padding=0)==[(0,2),(4,7),(8,10)]

def test_empty_silence():
    assert keep_intervals(10,[])==[(0,10)]

def test_timestamp():
    assert timestamp(3661.234)=='01:01:01,234'

def test_srt(tmp_path):
    p=tmp_path/'x.srt';write_srt([(0,1.5,'Hello')],p)
    assert '00:00:01,500' in p.read_text()

def test_short_segments():
    assert keep_intervals(1,[(0.1,0.9)],padding=0,min_clip=0.35)==[]
