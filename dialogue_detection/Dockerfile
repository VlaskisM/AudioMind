FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY dialogue_detection/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dialogue_detection/ ./dialogue_detection/

WORKDIR /app/dialogue_detection

CMD ["python", "run.py"]
