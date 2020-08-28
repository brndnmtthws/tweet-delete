FROM python:3-alpine

RUN apk add --no-cache --update build-base libffi-dev

WORKDIR /app
COPY . /app/src

RUN cd src \
  && pip install --no-cache-dir . \
  && apk del binutils libmagic file libgcc gcc musl-dev libc-dev g++ make fortify-headers build-base libffi-dev

ENTRYPOINT [ "tweet-delete" ]
