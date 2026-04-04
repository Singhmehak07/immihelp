FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/index_store

ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIR=/app/index_store

EXPOSE 8080

CMD ["python", "-m", "agent.main"]
