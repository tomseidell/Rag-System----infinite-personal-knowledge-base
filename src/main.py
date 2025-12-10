from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
# from src.user.model import User  
# from src.document.model import Document 
from src.core.exception_handlers import register_exception_handlers
from src.user.router import router as user_router
from src.document.router import router as document_router


app = FastAPI(
    title="FastAPI Project",
    description="A FastAPI project template",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add all exception handlers
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Project testrrrr"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(user_router, prefix="/user", tags=["users"])

app.include_router(document_router, prefix="/document", tags=["documents"])

if __name__ == "__main__":
    import uvicorn # webserser
    uvicorn.run(app, host="0.0.0.0", port=8000) # when we start python environment locally with main.py, this function gets called and starts the server
