FROM python:3.12.3-alpine


WORKDIR /backend
COPY . /backend

RUN apk add --no-cache wget \
    && wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz \
    && rm dockerize-linux-amd64-v0.6.1.tar.gz

RUN pip3 install -r requirements.txt

EXPOSE 8082

CMD ["dockerize", "-wait", "tcp://postgres:5432", "-wait", "tcp://redis:6379", "-timeout", "35s", "python3", "run.py"]

