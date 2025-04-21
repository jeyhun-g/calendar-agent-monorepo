import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from src.calendar_agent import create_calendar_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Load environment variables
load_dotenv()

# Application constants
APP_NAME = "calendar_chat_app"
USER_ID = "test_user"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize calendar agent components
    session_service = InMemorySessionService()
    calendar_agent = create_calendar_agent()
    runner = Runner(agent=calendar_agent, app_name=APP_NAME, session_service=session_service)

    # Create a new session for the application
    session_id = "new_session"
    session_service.create_session(session_id=session_id, app_name=APP_NAME, user_id=USER_ID)

    # Store services on app state for use in endpoints
    app.state.session_service = session_service
    app.state.runner = runner
    app.state.session_id = session_id

    yield
    # No explicit shutdown logic

app = FastAPI(lifespan=lifespan)
  
class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health():
    service_name = os.getenv("SERVICE_NAME")
    return {"service_name": service_name}
  
@app.post("/query")
async def query(request: QueryRequest):
    # Construct user content for the calendar agent
    content = types.Content(
        role="user",
        parts=[types.Part(text=request.query)]
    )

    # Retrieve runner and session info from app state
    runner = app.state.runner
    session_id = app.state.session_id

    # Execute the agent and capture the final response
    final_response = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    return {"response": final_response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )