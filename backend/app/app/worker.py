from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings
from app.transcriber import download_video, transcribe, format_transcription
from app import schemas
from time import sleep
from celery import shared_task, current_task
import logging
import json
from pathlib import Path
import datetime
import os

logger = logging.getLogger(__name__)
# client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"

def update_status( step, steps =100 , description=None) :
    logger.info(f"{step/steps:%} - {description}")
    current_task.update_state(
        state="PROGRESS",
        meta=schemas.Status(
                progress=step,
                totalAmount=steps,
                description=f"Working {step/steps:%}" if description is None else description,
                status="working",
                result=None,
            ).to_json(),
    )

@celery_app.task(acks_late=True)
def process_video(video=schemas.VideoRequest) -> schemas.Result:
    """
    Process video and return result.
    Currently just updates the status of the job every second sending Status object.
    At finish, sends Result object.

    """
    try:
        video = schemas.VideoRequest.parse_obj(video)
        logger.info(f"Processing video {video.url}\n {video.description}")
        dump_path = Path ("session_data/{date:%Y-%m-%d_%H:%M:%S}".format( date=datetime.datetime.now()))
        dump_path.mkdir(parents=True, exist_ok=True)

        update_status(0, description="Downloading video")
        audio_file = download_video(video.url,target_path=dump_path)
        update_status(10, description="Transcribing video")
        transcript = transcribe(audio_file)
        with (dump_path /"transcript.json").open("w") as f:
            json.dump(transcript, f)
        update_status(20, description="Formatting")
        vmarkdown = format_transcription(transcript, update_status, 20, 100, dump_path=dump_path)
        vmarkdown = f"\n?[]({video.url})\n\n{vmarkdown}" 
        
        res = schemas.Status(
            progress=100,
            totalAmount=100,
            description="All done!",
            status="finished",
            result=schemas.VmarkdownDocument(
                vmarkdown=vmarkdown
            ),
        )

        current_task.update_state(state="PROGRESS", meta=res.to_json())
        logger.info(f"finish {video.url}")
        return res.to_json()
    except Exception as e:
        logger.error(f"Error processing video {video.url}: {e}")
        # client_sentry.captureException()
        raise e
