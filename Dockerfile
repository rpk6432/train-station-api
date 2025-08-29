FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install gunicorn

WORKDIR /app

RUN addgroup -S appgroup && adduser -S -G appgroup appuser

RUN mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appgroup /app/media /app/staticfiles

COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000
