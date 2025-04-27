import os
from fastapi import FastAPI
from src.routers import events_router, health_router

app = FastAPI()
app.include_router(events_router.router)
app.include_router(health_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
