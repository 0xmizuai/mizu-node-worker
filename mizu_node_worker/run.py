import requests
import json
import logging
import os 

from dotenv import load_dotenv
from mizu_node_worker.classifier import classify
from mizu_node_worker.embeddings.domain_embeddings import V1_EMBEDDING

load_dotenv()

def run(take_job_url: str, finish_job_url: str, jwt: str):
    logging.basicConfig(level=logging.INFO)

    headers = {
        "Authorization": f"Bearer {jwt}",  # Typical format for JWT in headers
        "Content-Type": "application/json"  # Optional: specify JSON content type
    }

    while True:
        try:
            # Fetch the job from the queue
            response = requests.get(take_job_url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError if status is 4xx, 5xx
            response_data = response.json()

            print(response_data)

            job = response_data['data']['job']
            logging.info("Job Pulled. Processing now")

            job_type = job["jobType"]
            r2_url = job["r2Url"]

            if job_type != 1:
                logging.warning("Job type not supported")
                continue

            job_id = job["id"]
            raw_data_str = requests.get(r2_url).content
            raw_data = json.loads(raw_data_str)

            # Classify the data
            tags = classify(raw_data['text'], V1_EMBEDDING)
            tags_str = json.dumps(tags)

            # Post the result back to finish the job with signature and author
            logging.info("Classified. Posting Result Now")
            finish_response = requests.post(finish_job_url, headers=headers, json={
                "jobId": job_id,
                "result": tags_str,
            })
            finish_response.raise_for_status()  # Ensure the finish job request is successful
            logging.info("Job Done")

        except requests.RequestException as e:
            logging.error(f"Network error: {e}")
            continue

        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            continue

        except KeyError as e:
            logging.error(f"Missing key in the response data: {e}")
            continue

        except Exception as e:
            logging.critical(f"Unexpected error occurred: {e}")
            continue


base_url = os.environ.get("BASE_URL", "https://new-node.voda.build")
# "http://localhost:3033"
jwt = os.environ.get("JWT", "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaXp1LWFkbWluIiwiaWF0IjoxNzI5MjQ4MTg5LCJleHAiOjE3MjkzMzQ1ODl9.NNmz5ZL3RsqrFfpBQbANmSJzMv9OtDY7c8sOi_Y5bYJ_UXJpv_y1N9LbVsAujK62BSnlKVp20vXae3L_mKacBQ")

def start_worker():
    run(
        take_job_url = base_url + "/take_job?job_type=1",
        finish_job_url = base_url + "/finish_job",
        jwt = jwt,
    )

def start_validator():
    run(
        take_job_url = base_url + "/validate/take_job",
        finish_job_url = base_url + "/validate/finish_job",
        jwt = jwt,
    )