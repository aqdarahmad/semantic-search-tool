# ---------- Stage 1: build the React frontend ----------
FROM node:22-slim AS frontend-build

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: Python backend (serves the frontend too) ----------
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTEMBED_CACHE_PATH=/app/.fastembed

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model while building, so the server starts fast
RUN python -c "from fastembed import TextEmbedding; list(TextEmbedding('sentence-transformers/all-MiniLM-L6-v2').embed(['warm up']))"

COPY src ./src
COPY data/jobs ./data/jobs
COPY data/processed/candidate_profile.json ./data/processed/candidate_profile.json
COPY --from=frontend-build /build/dist ./frontend/dist

# Render sets PORT automatically (10000 by default)
EXPOSE 10000

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
