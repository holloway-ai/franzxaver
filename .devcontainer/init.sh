sudo apt-get update && sudo apt-get install ffmpeg libsm6 libxext6  -y
pipx install poetry
poetry config virtualenvs.create false && cd backend/app && poetry install --with=dev