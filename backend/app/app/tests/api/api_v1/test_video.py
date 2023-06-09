from typing import Dict
import json
import re
import codecs
import pytest
import asyncio
import time
from pydantic import parse_obj_as, parse_raw_as

from async_asgi_testclient import TestClient as AsyncTestClient


from app.core.config import settings
from app.schemas.video import Result, Status
from app.main import app

@pytest.mark.skip(reason="not a local test")
@pytest.mark.asyncio
async def test_video_all(
    api_token_headers:Dict[str, str]
) -> None:
    async with AsyncTestClient(app) as client:
        data = {
            "url": "http://franzxaver.holloway.ai/",
            "resultType": "vmarkdown",
            "description": "5"
        }
        response = await client.post(
            f"{settings.API_V1_STR}/video/",
            headers=api_token_headers,
            json=data,
        )
        assert response.status_code == 200
        content = response.json()
        assert "job_id" in content
        job_id = content["job_id"]
        
        response = await client.get(
        f"{settings.API_V1_STR}/video/{job_id}",
            headers=api_token_headers
        )
        assert response.status_code == 202
        stream_headers =api_token_headers
        stream_headers['Accept'] = 'text/event-stream'
        response = await client.get(f"{settings.API_V1_STR}/video/stream/{job_id}", headers=stream_headers, stream=True)
        decoder = codecs.getincrementaldecoder("utf8")(errors='replace')
        end_of_field = re.compile(r'\r\n\r\n|\r\r|\n\n')
        sse_json_pattern = re.compile(r"^\W?data:\W?\[\W?(?P<json>\{.*\})\W?\]\W?$",flags=re.MULTILINE)
        buffer = ""
        stream_result = None
        async for chunk in response.iter_content(chunk_size=None):
            line = chunk.decode('utf-8')
            print(line,time.strftime("%H:%M:%S", time.localtime()))
            m = sse_json_pattern.search(line)
            if m is not None:
                status = Status.parse_raw(m.group('json'))
                
                if status.result is not None:
                    stream_result = status.result
                    assert stream_result.resultType == "vmarkdown"
            
        response = await client.get(
        f"{settings.API_V1_STR}/video/{job_id}",
            headers=api_token_headers
        )
        assert response.status_code == 200
        
        job_result = parse_raw_as( Result,response.content)
        assert job_result.resultType == "vmarkdown"
        print(job_result.vmarkdown)
        print(stream_result.vmarkdown)
        assert job_result.vmarkdown[:10] == stream_result.vmarkdown[:10]
        assert job_result.vmarkdown == stream_result.vmarkdown
        