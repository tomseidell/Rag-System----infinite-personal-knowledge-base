# FastAPI Document Processing & Chat Application

A comprehensive FastAPI-based backend application for document processing, vector storage, and AI-powered chat capabilities. Built with modern Python technologies including async database operations, task queuing with Celery, vector search with Qdrant, and AI integration with Ollama.

## 🎯 Overview

This project provides a production-ready API for:
- **User Management**: Authentication, authorization, and user profiles
- **Document Processing**: Upload, parse, and chunk documents (PDFs supported)
- **Vector Storage**: Manage embeddings using Qdrant vector database
- **AI Chat**: Interactive chat with AI-powered responses
- **Task Queue**: Asynchronous document processing with Celery
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Rate Limiting**: Built-in request rate limiting middleware

## 📦 Tech Stack

### Core Framework
- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (0.24.0) - ASGI web server
- **Pydantic** (≥2.9) - Data validation and settings management

### Database & Storage
- **PostgreSQL** (15-alpine) - Primary relational database
- **SQLAlchemy** (2.0.23) - ORM with async support
- **Alembic** (1.12.1) - Database migrations
- **Redis** (7.1.0) - Caching and Celery broker
- **Qdrant** (latest) - Vector database for embeddings
- **Google Cloud Storage** - Document storage backend

### AI & NLP
- **Ollama** - Local LLM integration
- **LangChain Text Splitters** - Document chunking
- **FastEmbed** - Embedding generation
- **PyPDF**, **PyMuPDF** - PDF processing

### Task Processing
- **Celery** (5.6.0) - Distributed task queue
- **Redis** - Message broker and result backend

### Monitoring & Observability
- **Prometheus** - Metrics collection
- **Prometheus FastAPI Instrumentator** - FastAPI metrics middleware
- **Grafana** - Visualization dashboards

### Security & Utilities
- **Passlib** - Password hashing
- **PyJWT** - JWT token handling
- **Bcrypt** - Cryptographic hashing
- **Email Validator** - Email validation
- **Python Dotenv** - Environment variable management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (if running without Docker)
- Redis (if running without Docker)

### Local Setup (without Docker)

1. **Clone the repository and navigate to the project:**
```bash
cd /path/to/fastApiProject
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a `.env` file with required environment variables:**
```bash
ENVIRONMENT=development
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_PORT=5432
DB_NAME=fastapi_db
DB_HOST=localhost

GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

JWT_SECRET=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
```

5. **Initialize the database:**
```bash
alembic upgrade head
```

6. **Run the application:**
```bash
python src/main.py
```
or
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup (Recommended)

1. **Ensure Docker and Docker Compose are installed**

2. **Create a `.env` file** (see above)

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Run database migrations:**
```bash
docker-compose exec api alembic upgrade head
```

Services will be available at:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **PgAdmin**: http://localhost:5050 (admin@admin.com / admin)
- **Qdrant Vector DB**: http://localhost:6333
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI (OpenAPI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics (Prometheus format)

### Available Endpoints

#### Health & Root
- `GET /` - Welcome message
- `GET /health` - API health check

#### User Management (`/user`)
- User registration, login, and profile management
- JWT-based authentication
- Token refresh mechanism

#### Document Management (`/document`)
- Upload documents
- Process and chunk documents
- Retrieve document metadata
- Support for PDF files with text extraction
- Asynchronous processing with Celery workers

#### Chat (`/chat`)
- Interactive chat with AI
- Context-aware responses using vector search
- Integration with Ollama LLM

## 🏗️ Project Structure

```
fastApiProject/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── routes.py                    # Main router configuration
│   ├── config.py                    # Settings management
│   ├── database.py                  # Database engine and session setup
│   ├── clients/                     # External service clients
│   │   ├── ollama/                  # Ollama LLM integration
│   │   ├── qdrant/                  # Vector database client
│   │   ├── redis/                   # Redis caching client
│   │   └── storage/                 # GCS file storage client
│   ├── core/                        # Core application logic
│   │   ├── celery_app.py            # Celery task queue setup
│   │   ├── exception_handlers.py    # Global exception handlers
│   │   ├── exceptions.py            # Custom exception classes
│   │   └── middleware/
│   │       └── rate_limit.py        # Rate limiting middleware
│   └── modules/                     # Feature modules
│       ├── user/                    # User management
│       ├── document/                # Document processing
│       ├── chunk/                   # Document chunking
│       └── chat/                    # Chat functionality
├── alembic/                         # Database migrations
│   └── versions/                    # Migration files
├── docker-compose.yaml              # Docker services configuration
├── Dockerfile                       # Container image definition
├── requirements.txt                 # Python dependencies
├── prometheus.yml                   # Prometheus configuration
├── alembic.ini                      # Alembic configuration
└── .env                             # Environment variables (not in repo)
```

## 📊 Monitoring & Observability

### Prometheus Metrics
- Metrics are automatically collected from all FastAPI endpoints
- Available at `/metrics` endpoint
- Prometheus scrapes metrics every 15 seconds (configurable in `prometheus.yml`)

### Grafana Dashboards
- Access Grafana at http://localhost:3000
- Add Prometheus as a data source (http://prometheus:9090)
- Create custom dashboards for monitoring

### Sample Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Request duration
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_exceptions_total[5m])
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt-based password storage
- **Rate Limiting**: Request rate limiting to prevent abuse
- **CORS Configuration**: Configurable Cross-Origin Resource Sharing
- **Environment Variables**: Sensitive data stored in `.env` file
- **Google Cloud Integration**: Secure storage with GCS

## 🔄 Async & Task Processing

### Celery Workers
Asynchronous task processing for long-running operations:

```bash
# Start a Celery worker
celery -A src.core.celery_app worker --loglevel=info --queues=documents

# Monitor tasks
celery -A src.core.celery_app events
```

The Docker setup includes:
- **API Service**: Main FastAPI application
- **Worker Service**: Celery worker for document processing
- **Redis**: Message broker and result backend

## 🚦 Rate Limiting

The application includes built-in rate limiting middleware:
- Configurable per endpoint
- Redis-backed for distributed systems
- Prevents abuse and ensures fair resource usage

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `development`, `production` |
| `DATABASE_USER` | PostgreSQL username | `postgres` |
| `DATABASE_PASSWORD` | PostgreSQL password | `secure_password` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `fastapi_db` |
| `DB_HOST` | Database host | `localhost`, `db` |
| `DB_POOL_SIZE` | Connection pool size | `16` |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | `my-bucket` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCS credentials | `./credentials.json` |
| `JWT_SECRET` | JWT signing secret | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token TTL | `43200` |


---

**Last Updated**: January 30, 2026
