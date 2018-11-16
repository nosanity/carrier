FROM python:3.7-alpine3.8
RUN apk add --no-cache --virtual .tmp_deps build-base python3-dev libffi-dev openssl-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w 4", "-k aiohttp.GunicornWebWorker", "-b 0.0.0.0:8080", "app.main:container()"]