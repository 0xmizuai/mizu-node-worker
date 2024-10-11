from typing import Union

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AIRuntimeConfig(BaseModel):
    pass

class ClassificationJob(BaseModel):
    text: str
    config: Union[AIRuntimeConfig, None] = None


class ClassificationResult(BaseModel):
    output: str
    job_id: str
    version: int = 0


def classifier(text: str, config: Union[AIRuntimeConfig, None], job_id: str) -> ClassificationResult:
    """This is a mock function"""
    print(f"{config=}")
    return ClassificationResult(output=text[::-1], job_id=job_id)


@app.post("/verifyJob/{job_id}")
async def verify_job(job_id: str, payload: ClassificationJob):
    return classifier(payload.text, payload.config, job_id)

def start_dev():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000, reload=True)

# the number of workers is defined by $WEB_CONCURRENCY env as default
def start():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000)