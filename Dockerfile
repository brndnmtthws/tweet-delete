FROM python:3-alpine

RUN apk add --no-cache --update build-base libffi-dev openssl-dev

WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir poetry \
  && poetry install --no-dev \
  && apk del binutils libmagic file libgcc gcc musl-dev libc-dev g++ make fortify-headers build-base libffi-dev openssl-dev

COPY . /app
RUN poetry install --only main --no-root

ENTRYPOINT ["poetry", "run", "tweet-delete"]
