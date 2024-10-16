# Validator

## Installation and usage


### Install

```shell
git clone <this repo> validator
cd validator
poetry install
poetry run pre-commit install
```

### Run

The environment variable `REDIS_URL` controls where the job requests are queued.  
If not set, it defaults to `localhost:6379`.

#### Start the http server:
```shell
poetry run dev # for dev
poetry run start # for prod
```

#### Start a RQ worker

The worker needs additional enironment variables to access R2:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- CLOUDFLARE_R2_ID
- CLOUDFLARE_R2_BUCKET_NAME

```shell
poetry run start_worker
```
There is no need to start a worker on the same machine, as long as there is at least
another worker listening on the same redis server and queue.  
Otherwise no jobs will ever complete.
