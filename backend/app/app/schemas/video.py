from typing import Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, AnyHttpUrl, ValidationError
from fastapi.encoders import jsonable_encoder


class JsonBaseModel(BaseModel):
    def to_json(self):
        return jsonable_encoder(self)

class DocumentTypeEnum(str, Enum):
    vmarkdown ="vmarkdown"
    html="html"

# Video request properties
class VideoRequest(JsonBaseModel):
    url: AnyHttpUrl
    resultType: DocumentTypeEnum 
    description: Optional[str] = None



# Job token
class Job(BaseModel):
    job_id: str


class JobStatusEnum(str, Enum):
    working = "working"
    finished = "finished"
    error = "error"



    
class BaseDocument(JsonBaseModel):
    resultType: DocumentTypeEnum 

class VmarkdownDocument(BaseDocument):
    resultType: DocumentTypeEnum = DocumentTypeEnum.vmarkdown
    vmarkdown: str

class HtmlDocument(BaseDocument):
    resultType: DocumentTypeEnum = DocumentTypeEnum.html
    html: str
    
    


# Job result
Result = Union[VmarkdownDocument, HtmlDocument]


# Status of the job
class Status(JsonBaseModel):
    progress: int
    totalAmount: int
    description: str
    status: JobStatusEnum
    result: Optional[Result] = None