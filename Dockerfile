FROM python:latest

WORKDIR .

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . .



