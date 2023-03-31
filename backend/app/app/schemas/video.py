from typing import Optional, Any
from enum import Enum

from pydantic import BaseModel, AnyHttpUrl, ValidationError
from fastapi.encoders import jsonable_encoder


# Video request properties
class Video(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None
    def to_json(self):
        return jsonable_encoder(self)


# Job token
class Job(BaseModel):
    job_id: str


class JobStatusEnum(str, Enum):
    working = "working"
    finished = "finished"
    error = "error"


# Status of the job
class Status(BaseModel):
    progress: int
    totalAmount: int
    description: str
    status: JobStatusEnum
    result: Optional[Any] = None
    def to_json(self):
        return jsonable_encoder(self)

# Job result
class Result(BaseModel):
    result: Any
    def to_json(self):
        return jsonable_encoder(self)