import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    service_name = os.getenv("SERVICE_NAME")
    return {"service_name": service_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )