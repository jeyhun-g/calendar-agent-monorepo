import os

from pydantic import BaseModel
from dotenv import load_dotenv

from src.calendar_agent import create_calendar_agent
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types

from src.server import init_server

# Load environment variables
load_dotenv()

# Application constants
APP_NAME = "calendar_chat_app"
USER_ID = "test_user"

db = {
    "user": os.getenv("DB_USER"),
    "pwd": os.getenv("DB_PWD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

calendar_agent = create_calendar_agent()
session_service = DatabaseSessionService(f"postgresql://{db['user']}:{db['pwd']}@{db['host']}:{db['port']}")
app = init_server(app_name=APP_NAME, calendar_agent=calendar_agent, session_service=session_service)
  
class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str

class SessionRequest(BaseModel):
    user_id: str

@app.get("/health")
async def health():
    service_name = os.getenv("SERVICE_NAME")
    return { "service_name": service_name, "status": "okay" }

@app.post("/session")
async def session(request: SessionRequest):
    session = session_service.create_session(app_name=APP_NAME, user_id=request.user_id)
    return { "session_id": session.id }
  
@app.post("/query")
async def query(request: QueryRequest):
    # Construct user content for the calendar agent
    content = types.Content(
        role="user",
        parts=[types.Part(text=request.query)]
    )

    # Retrieve runner and session info from app state
    runner = app.state.runner
    session_id = request.session_id

    # Execute the agent and capture the final response
    final_response = ""
    async for event in runner.run_async(
        user_id=request.user_id,
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