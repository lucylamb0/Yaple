FROM ubuntu:latest
LABEL authors="lucy"
FROM python:3.13-slim
RUN mkdir /Yaple
WORKDIR /Yaple
COPY . /Yaple
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
