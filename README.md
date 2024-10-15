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

Start the http server:
```shell
poetry run dev # for dev
poetry run start # for prod
```

Start a RQ worker
```shell
poetry run start_worker
```
There is no need to start a worker on the same machine, as long as there is at least
another worker listening on the same redis server and queue.  
Otherwise no jobs will ever complete.
