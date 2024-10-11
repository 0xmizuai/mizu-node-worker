import time

from typing import Union

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
def verify_job(job_id: str, payload: ClassificationJob):
    return classifier(payload.text, payload.config, job_id)
