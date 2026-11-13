# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Requirements File Is UTF-16 LE; Normalize It For Pip.
RUN python -c "from pathlib import Path; Path('/tmp/requirements.txt').write_text(Path('requirements.txt').read_text(encoding='utf-16'), encoding='utf-8')"

RUN pip install --upgrade pip \
    && pip install --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r /tmp/requirements.txt \
    && pip install gunicorn==23.0.0

RUN python -m spacy download en_core_web_sm

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    NLTK_DATA=/usr/local/share/nltk_data \
    DJANGO_SETTINGS_MODULE=mamachef.settings

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 nginx \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --create-home app

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY --chown=app:app . .

RUN SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && python -m nltk.downloader -d /usr/local/share/nltk_data wordnet omw-1.4 \
    && mkdir -p /app/media \
    && sed -i 's/\r$//' /app/docker-entrypoint.sh /app/nginx.conf \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R app:app /app /usr/local/share/nltk_data

USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
