FROM python:3.7-alpine3.8

LABEL maintainer="Nick Lubyanov <lubyanov@gmail.com>"
MAINTAINER NickLubyanov "lubyanov@gmail.com"

RUN apk add --no-cache --virtual .tmp_deps build-base python3-dev libffi-dev openssl-dev curl busybox-extras bash

COPY . /app
WORKDIR /app

#RUN pip install -r requirements.txt
ENTRYPOINT ["./docker-entrypoint.sh" ]

# changed to '-w 1' while some concurrent bugs are exist
CMD ["gunicorn", "-w 1", "-k aiohttp.GunicornWebWorker", "-b 0.0.0.0:80", "app.main:container()"]