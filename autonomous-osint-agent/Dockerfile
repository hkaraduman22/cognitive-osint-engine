FROM python:3.12-slim

WORKDIR /app

COPY autonomous-osint-agent/core-api/requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir ddgs

COPY autonomous-osint-agent/core-api/ ./core-api/
COPY scraper-bot/ ./scraper-bot/
COPY analiz.py ./analiz.py
COPY redis_listener.py ./redis_listener.py
WORKDIR /app/core-api

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
