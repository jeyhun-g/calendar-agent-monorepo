from dotenv import load_dotenv
load_dotenv()

import hashlib
import os
import httpx

from mcp.server.fastmcp import FastMCP
from typing import Optional

def convert_to_event_id(event_name: str) -> str:
  return hashlib.sha256(event_name.encode("utf-8")).hexdigest()

config = {
  "base_url": os.getenv("CALENDAR_API_BASE_URL")
}

# Create an MCP server
mcp = FastMCP("CalendarMCP", settings={
  "host": "0.0.0.0",
  "port":  os.getenv("PORT") or 8080
})

@mcp.tool()
async def create_event(
  event_name: str, 
  event_time: str, 
  duration_in_minutes: int, 
  location: Optional[str]
):
  """
  Create new event
  """
  try:
    async with httpx.AsyncClient() as client:
        payload = {
          "event_name": event_name,
          "event_time": event_time,
          "duration_in_minutes": duration_in_minutes,
          "location": location,
        }
        response = await client.post(f"{config['base_url']}/events", json=payload)
        response.raise_for_status()
        return "Success"
  except httpx.HTTPError as e:
    return f"Error: {e}"

@mcp.tool()
async def delete_event(event_name: str) -> int:
  """
  Delete an event
  """
  try:
    event_id = convert_to_event_id(event_name)
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{config['base_url']}/events/{event_id}")
        response.raise_for_status()
        return "Success"
  except httpx.HTTPError as e:
    return f"Error: {e}"

@mcp.tool()
async def update_event(
  old_event_name: str, 
  new_event_name: Optional[str], 
  event_time: Optional[str], 
  duration_in_minutes: Optional[int], 
  location: Optional[str]
  ):
  """
  Update an event
  """
  try:
    event_id = convert_to_event_id(old_event_name)
    async with httpx.AsyncClient() as client:
        payload = {
          "event_name": new_event_name,
          "event_time": event_time,
          "duration_in_minutes": duration_in_minutes,
          "location": location,
        }
        response = await client.patch(f"{config['base_url']}/events/{event_id}", json=payload)
        response.raise_for_status()
        return response.json()
  except httpx.HTTPError as e:
    return f"Error: {e}"

@mcp.tool()
async def get_all_events():
  """
  List all events
  """
  try:
    async with httpx.AsyncClient() as client:
      response = await client.get(f"{config['base_url']}/events")
      response.raise_for_status()
      return response.json()
  except httpx.HTTPError as e:
    return f"Error: {e}"
  
@mcp.tool()
async def get_all_events(event_name: str):
  """
  Get single event
  """
  try:
    event_id = convert_to_event_id(event_name)
    async with httpx.AsyncClient() as client:
      response = await client.get(f"{config['base_url']}/events/{event_id}")
      response.raise_for_status()
      return response.json()
  except httpx.HTTPError as e:
    return f"Error: {e}"


if __name__ == "__main__":
  print("Running mcp server")
  mcp.run(transport='sse')
