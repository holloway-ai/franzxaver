import pytest
from pathlib import Path
import datetime


@pytest.fixture
def dump_path():
    path = Path(
        "session_data/{date:%Y-%m-%d_%H:%M:%S}".format(date=datetime.datetime.now())
    )
    path.mkdir(parents=True, exist_ok=True)
    yield path
    # path.rmdir()
