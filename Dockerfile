FROM python:3.11-slim AS echobot

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus-dev \
    libsodium-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
