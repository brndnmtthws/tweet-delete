FROM python:3-alpine

RUN apk add --no-cache --update build-base libffi-dev openssl-dev

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip \
  && pip install poetry \
  && poetry install --no-dev \
  && apk del binutils libmagic file libgcc gcc musl-dev libc-dev g++ make fortify-headers build-base libffi-dev openssl-dev

ENTRYPOINT ["poetry", "run", "tweet-delete"]
