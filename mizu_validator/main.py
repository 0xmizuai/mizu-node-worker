from typing import Union

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING
from mizu_validator.classifier import classify

import requests

app = FastAPI()


class AIRuntimeConfig(BaseModel):
    debug: bool = False
    callback_url: str = None


class ClassificationJob(BaseModel):
    job_id: str
    text: str
    config: Union[AIRuntimeConfig, None] = None


@app.post("/classify")
async def do_classify(job: ClassificationJob):
    tags = classify(job.text, V1_EMBEDDING)
    requests.post(
        job.config.callback_url,
        json={"job_id": job.job_id, "tags": tags},
    )


def start_dev():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000, reload=True)


# the number of workers is defined by $WEB_CONCURRENCY env as default
def start():
    uvicorn.run("mizu_validator.main:app", host="0.0.0.0", port=8000)
