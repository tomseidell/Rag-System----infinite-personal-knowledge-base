from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # fast api middleware ist direkt als middleware in fastapi accessible 

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

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Project testrrrr"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # when we start python environment locally with main.py, this function gets called and starts the server
