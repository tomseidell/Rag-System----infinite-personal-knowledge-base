from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator # prometheus client wrapper: https://github.com/trallnag/prometheus-fastapi-instrumentator
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from api.middlewares.rate_limit import rate_limit_middleware


ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
from shared.core.exception_handlers import register_exception_handlers
from api.clients.qdrant.dependencies import get_qdrant_service
from api.routes import router as routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Qdrant Service...")
    get_qdrant_service()
    print("Qdrant Service initialized")
    yield

app = FastAPI(
    title="FastAPI Project",
    description="A FastAPI project template",
    version="1.0.0",
    lifespan=lifespan
)

app.middleware("http")(rate_limit_middleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = Instrumentator(
    excluded_handlers=["/metrics"] # exclude / metrics endpoint for metrics in prometheus 
)

# middleware in our application, tracking every request and mapping it to /metrics
instrumentator.instrument(app).expose(app, include_in_schema=False,) # dont show in /docs



# add all exception handlers
register_exception_handlers(app)


app.include_router(routes)



if __name__ == "__main__":
    import uvicorn # webserser
    uvicorn.run(app, host="0.0.0.0", port=8000) # when we start python environment locally with main.py, this function gets called and starts the server
