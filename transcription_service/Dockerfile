FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY transcription_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY transcription_service/ ./transcription_service/

WORKDIR /app/transcription_service

CMD ["python", "run.py"]
