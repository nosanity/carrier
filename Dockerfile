FROM python:3.7-alpine3.8

LABEL maintainer="Nick Lubyanov <lubyanov@gmail.com>"
MAINTAINER NickLubyanov "lubyanov@gmail.com"

EXPOSE 80
WORKDIR /opt
ENTRYPOINT ["./docker-entrypoint.sh" ]
CMD gunicorn -w 1 -k aiohttp.GunicornWebWorker -b 0.0.0.0:80 app.main:container
# changed to '-w 1' while some concurrent bugs are exist

RUN apk add --no-cache --virtual .tmp_deps build-base python3-dev libffi-dev openssl-dev && \
    apk add -u curl busybox-extras

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD gunicorn -w 1 -k aiohttp.GunicornWebWorker -b 0.0.0.0:80 app.main:container
#CMD gunicorn -w 3 -b 0.0.0.0:80 wsgi:application