FROM python:3.11-slim

# Instalar nmap y dependencias de reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap gcc libfreetype6-dev libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY config /app/config
COPY data /app/data

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/src/main.py", "--schedule"]
