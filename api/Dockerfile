FROM python:3.12-slim

WORKDIR /app


# remove pyc files and add uvicorn logs
# define cache path for huggingface manually
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create user for application with --system config 
RUN useradd --system --uid 1001 api \
    && mkdir -p /app/.cache/huggingface \
    && chown -R api:api /app/.cache

# select user for container
USER api

# start app as user : api 
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 

