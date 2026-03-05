FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_ingress/ ./data_ingress/

WORKDIR /app/data_ingress

CMD ["uvicorn", "src.web.web:app", "--host", "0.0.0.0", "--port", "8000"]
