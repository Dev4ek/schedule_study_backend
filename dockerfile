FROM python:alpine

WORKDIR /backend

COPY . /backend

RUN pip3 install -r requirements.txt

EXPOSE 8021

CMD [ "python3", "run.py" ]

