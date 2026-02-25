FROM python:3.13-slim-bullseye AS builder

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev-compat \
    libssl-dev \ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

COPY src/ ./src/

RUN mkdir -p /app/src/hpc_drive/uploads

EXPOSE 7777

ENV PYTHONPATH=/app
ENV UPLOADS_DIR=/app/src/hpc_drive/uploads
ENV DATABASE_URL="sqlite:////app/data/drive.db"
ENV AUTH_SERVICE_ME_URL="http://auth_service:8082/api/v1/me"

CMD ["uvicorn", "--app-dir", "src", "hpc_drive.main:app", "--host", "0.0.0.0", "--port", "7777" ""]
