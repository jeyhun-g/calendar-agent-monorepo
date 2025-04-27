import hashlib
import os

from fastapi import FastAPI, HTTPException, status
from typing import Optional
from pydantic import BaseModel

class Event(BaseModel):
    event_name: str
    event_time: str
    duration_in_minutes: int
    location: Optional[str] = None

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    event_time: Optional[str] = None
    duration_in_minutes: Optional[int] = None
    location: Optional[str] = None

# Key-value in memeory storage for events
# key = hash of the event name
events = {}
 
def convert_to_event_id(event_name: str) -> str:
  return hashlib.sha256(event_name.encode("utf-8")).hexdigest()


# Create the FastAPI server
app = FastAPI()

@app.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event):
    """
    Create new event
    """
    event_id = convert_to_event_id(event.event_name)
    if event_id in events:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict: event exists")

    event_data = event.model_dump(exclude_unset=True)
    events[event_id] = event_data
    return { "event_id": event_id, **event_data}

@app.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """
    Delete an event
    """
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not Found: Event doesn't exist")

    del events[event_id]

@app.patch("/events/{event_id}", status_code=status.HTTP_200_OK)
async def update_event(event_id: str, event: EventUpdate):
    """
    Partial update of an event. Only provided fields will be modified.
    """
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not Found: Event doesn't exist")

    current_event = events[event_id]
    data = event.model_dump(exclude_unset=True)

    if "event_name" in data:
        new_id = convert_to_event_id(data["event_name"])
        del events[event_id]
        event_id = new_id
        current_event["event_name"] = data["event_name"]

    for field in ("event_time", "duration_in_minutes", "location"):
        if field in data:
            current_event[field] = data[field]

    events[event_id] = current_event
    return { "event_id": event_id, **current_event}

@app.get("/events", status_code=status.HTTP_200_OK)
async def get_all_events():
    """
    List all events
    """
    # Return all events with their IDs
    return [{"event_id": eid, **edata} for eid, edata in events.items()]

@app.get("/events/{event_id}", status_code=status.HTTP_200_OK)
async def get_event(event_id: str):
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found: Event doesn't exist")
    
    return { "event_id": event_id, **events[event_id]}

@app.get("/health")
async def health():
    return { "service_name": "calendar_api", "status": "okay" }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
