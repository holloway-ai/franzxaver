import datetime
from pathlib import Path
from urllib.request import urlopen
import pytest
import json

data_path = Path("test_data/pydata")
video_path = data_path / "video.mkv"
audio_path = data_path / "audio.mp4"
# transcript_path = data_path / "transcript_short.json"
transcript_path = data_path / "transcript.json"
slides_path = data_path / "slides.json"
markdown_path = data_path / "result.md"
video_url = "https://youtu.be/gUNWHrSxbBY"


def test_download(dump_path):
    from app.transcriber import download_video

    download_video(video_url, dump_path)
    assert (dump_path / "video.mkv").exists()
    assert (dump_path / "audio.mp4").exists()


def test_slides(dump_path):
    from app.transcriber import extract_and_save_slides

    results = extract_and_save_slides(video_path, dump_path)
    assert len(results) > 3
    with urlopen(results[-1][1]) as response:
        info = response.info()
        assert info.get_content_type() == "image/png"
    with (dump_path / "slides.json").open("w") as f:
        json.dump(results, f, indent=4)


def test_transcribe(dump_path):
    from app.transcriber import transcribe

    results = transcribe(audio_path)
    assert len(results) > 0
    with (dump_path / "transcript.json").open("w") as f:
        json.dump(results, f, indent=4)


def test_format(dump_path):
    from app.transcriber import format_transcription

    with transcript_path.open() as f:
        transcript = json.load(f)
    with slides_path.open() as f:
        slides = json.load(f)

    results = format_transcription(transcript, dump_path=dump_path, slides=slides)
    last_line = transcript["segments"][-1]["text"]
    assert results.find(last_line) > 0
    assert len(results) > 0


def test_insert_slides():
    from app.transcriber.vmarkdown import insert_slides

    with slides_path.open() as f:
        slides = json.load(f)
    with markdown_path.open() as f:
        text = f.read()
    results = insert_slides(text, slides)
    assert len(results) > 0
    assert results.find(slides[-1][1]) > 0
    assert results.find(slides[0][1]) > 0
