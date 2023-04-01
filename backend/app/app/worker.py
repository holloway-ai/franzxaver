from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings
from app import schemas
from time import sleep
from celery import shared_task, current_task
import logging

logger = logging.getLogger(__name__)
#client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(acks_late=True)
def process_video (video = schemas.VideoRequest) -> schemas.Result:
    """
    Process video and return result.
    Currently just updates the status of the job every second sending Status object.
    At finish, sends Result object.
    
    """
    logger.info("Processing video {video.url}}")
    
    for i in range(100):
         
        current_task.update_state(
            state="PROGRESS",
            meta=schemas.Status(
                progress=i,
                totalAmount=100,
                description=f"Working {i/100}",
                status="working",
                result=None,
            ).to_json()
        )
        logger.info("update_state {video.url}}")
        sleep(1)
    res = schemas.VmarkdownDocument(vmarkdown = "Video markdown here\n but I am not sure yet.")
    current_task.update_state(
            state="PROGRESS",
            meta=schemas.Status(
                progress=i,
                totalAmount=100,
                description="All done!",
                status="finished",
                result=res.vmarkdown,
                
            ).to_json()
    )
    logger.info("finish {video.url}}")
    return res.to_json()

