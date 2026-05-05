FROM python:3.12-slim

WORKDIR /app 

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

CMD ["sh", "-c", "if [ \"$WORKER_TYPE\" = 'pdf_reader' ]; then celery -A worker.celery_app worker --loglevel=info -Q pdf_read --concurrency=1; else celery -A worker.celery_app worker --loglevel=info -Q embed --concurrency=1; fi"]