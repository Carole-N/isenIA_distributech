# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

# Pas de .pyc, logs non-bufferisés
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Créer un utilisateur non-root
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/usr/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Installer les dépendances Python (avec cache pip) à partir de requirements.txt
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code
COPY . .

# Exécuter en utilisateur non-root
USER appuser

# Commande par défaut : lance le pipeline ETL (modifiable dans Compose)
CMD ["python", "etl.py"]
