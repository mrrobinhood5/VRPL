# syntax=docker/dockerfile:1
FROM python:3.10.1

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt update

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY . .

CMD [ "python3", "main.py" ]