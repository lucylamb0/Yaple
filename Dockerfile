FROM ubuntu:latest
LABEL authors="lucy"
FROM python:3.13-slim
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
