import requests

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from mizu_validator.classifier import classify
from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING
from mizu_validator.r2 import get_decoded_value


class AIRuntimeConfig(BaseModel):
    debug: bool = False
    callback_url: str = None


class ClassificationJob(BaseModel):
    job_id: str
    r2_key: str
    config: AIRuntimeConfig | None = None


class ClassificationResult(BaseModel):
    job_id: str
    tags: list[str]


def classification_worker(job: ClassificationJob):
    text = get_decoded_value(job.r2_key)
    tags = classify(text, V1_EMBEDDING)
    reply = ClassificationResult(job_id=job.job_id, tags=tags)
    requests.post(
        job.config.callback_url,
        json=jsonable_encoder(reply),
    )
