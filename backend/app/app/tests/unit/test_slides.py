import datetime
from pathlib import Path
from urllib.request import urlopen


def test_slides():
    from app.transcriber import (
        download_video,
        extract_and_save_slides,
    )

    dump_path = Path(
        "session_data/{date:%Y-%m-%d_%H:%M:%S}".format(date=datetime.datetime.now())
    )
    dump_path.mkdir(parents=True, exist_ok=True)
    video_path, audio_path = download_video(
        "https://youtu.be/1_j6quv13Rk", target_path=dump_path
    )
    results = extract_and_save_slides(video_path, dump_path)
    with urlopen(results[-1][1]) as response:
        info = response.info()
        assert info.get_content_type() == "image/png"
