import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Placeholder for startup logic
    yield
    # Placeholder for shutdown logic

app = FastAPI(lifespan=lifespan)
  
class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health():
    service_name = os.getenv("SERVICE_NAME")
    return {"service_name": service_name}
  
@app.post("/query")
async def query(request: QueryRequest):
    return {"query": request.query}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )