from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from sse_starlette.sse import EventSourceResponse
import asyncio
from celery.result import AsyncResult
from app.core.celery_app import celery_app

from fastapi.security.api_key import APIKey


router = APIRouter()



@router.post("/", response_model=schemas.Job)
def transcribe(
    *,
    video: schemas.VideoRequest,
    api_key: APIKey = Depends(deps.get_api_key),
) -> Any:
    job = celery_app.send_task("app.worker.process_video", args=[video.to_json()])
    return schemas.Job(job_id=job.id)

@router.get("/{job_id}", response_model=schemas.Result)
def get_result_by_id(
    job_id: str,
    api_key: APIKey = Depends(deps.get_api_key),
) -> Any:
    task = celery_app.AsyncResult(job_id)
    if not task.ready():
        raise HTTPException(status_code=202, detail=f"Job is still {task.state}")
    status = schemas.Status.parse_obj(task.result)
    return status.result

STREAM_DELAY = 1  # second


@router.get('/stream/{job_id}')
async def message_stream(
    job_id: str,
    request: Request,
    api_key: APIKey = Depends(deps.get_api_key),

):
    task = AsyncResult(job_id)
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            
            yield [schemas.Status.parse_obj(task.info).json()]
            if task.ready():
                break
            await asyncio.sleep(STREAM_DELAY)
            
            
    return EventSourceResponse(event_generator())