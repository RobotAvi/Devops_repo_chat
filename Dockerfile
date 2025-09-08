FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional: git for debugging, build tools for faiss)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src ./src
COPY Makefile ./Makefile
COPY README.md ./README.md
COPY .env.example ./.env.example
COPY templates ./templates
COPY static ./static

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.chat_interface:app", "--host", "0.0.0.0", "--port", "8000"]

