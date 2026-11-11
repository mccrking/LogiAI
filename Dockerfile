FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOGIAI_HOME=/app

COPY requirements-runtime.txt ./
RUN pip install --no-cache-dir -r requirements-runtime.txt \
    && useradd --uid 10001 --create-home logiai

COPY logiai/ ./logiai/

# Étape facultative pour préparer les artefacts sans Python installé sur l'hôte.
FROM base AS trainer
CMD ["sh", "-c", "python -m logiai.dataset && python -m logiai.train"]

FROM base AS runtime
COPY data/ ./data/
COPY models/ ./models/

USER logiai
EXPOSE 8000
CMD ["uvicorn", "logiai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
