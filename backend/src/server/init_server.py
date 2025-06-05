import asyncio

from contextlib import asynccontextmanager
from google.adk.agents import LlmAgent

from fastapi import FastAPI
from starlette.datastructures import State

from google.adk.sessions import BaseSessionService
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from typing import Optional

class AppState(State):
    session_service: Optional[BaseSessionService] = None
    runner: Optional[Runner] = None

class CalendarFastAPI(FastAPI):
    state: AppState

def init_server(app_name: str, session_service: BaseSessionService, calendar_agent: LlmAgent):
  @asynccontextmanager
  async def lifespan(app: FastAPI):
    tools, exit_stack = await asyncio.create_task(MCPToolset.from_server(
      connection_params=SseServerParams(
          url="http://0.0.0.0:8080/sse"
      ))
    )

    calendar_agent.tools = tools

    runner = Runner(agent=calendar_agent, app_name=app_name, session_service=session_service)

    # Store services on app state for use in endpoints
    app.state.session_service = session_service
    app.state.runner = runner

    yield
    
    await asyncio.create_task(exit_stack.aclose())

  app = CalendarFastAPI(lifespan=lifespan)
  return app