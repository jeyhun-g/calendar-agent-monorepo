import os
from contextlib import asynccontextmanager

from pydantic import BaseModel
from dotenv import load_dotenv

from src.calendar_agent import create_calendar_agent
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .src.server import init_server

# Load environment variables
load_dotenv()

# Application constants
APP_NAME = "calendar_chat_app"
USER_ID = "test_user"

calendar_agent = create_calendar_agent()
session_service = InMemorySessionService()
app = init_server(app_name=APP_NAME, calendar_agent=calendar_agent, session_service=session_service)
  
class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health():
    service_name = os.getenv("SERVICE_NAME")
    return { "service_name": service_name, "status": "okay" }
  
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

    return { "response": final_response }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )