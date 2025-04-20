from src.calendar_agent import create_calendar_agent
import asyncio

from dotenv import load_dotenv
load_dotenv()

from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.adk.runners import Runner
from google.genai import types

from typing import AsyncGenerator

APP_NAME = "calendar_chat_app"
USER_ID = "test_user"


session_service = InMemorySessionService()
calendar_agent = create_calendar_agent()
runner = Runner(agent=calendar_agent, app_name=APP_NAME, session_service=session_service)

async def execute_agent(session_id: str, query: str) -> AsyncGenerator[Event, None]:
  content = types.Content(role='user', parts=[types.Part(text=query)])
  async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
      yield event

async def run():
  session_id = "new_session"
  session_service.create_session(session_id=session_id, app_name=APP_NAME, user_id=USER_ID)

  while True:
    user_query = input("Query:")
    async for event in execute_agent(session_id, user_query):
      if event.is_final_response():
            print("Agent Response: ", event.content.parts[0].text)


asyncio.run(run())

    