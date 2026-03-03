FROM python:latest AS echobot

RUN apt update && apt install -y ffmpeg libopus-dev

WORKDIR /app
COPY . /app

RUN pip install --upgrade --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
