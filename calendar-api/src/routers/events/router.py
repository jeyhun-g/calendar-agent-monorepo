import hashlib

from fastapi import APIRouter, HTTPException, status

from .models import Event, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])

# In-memory storage for events
events = {}

def convert_to_event_id(event_name: str) -> str:
    return hashlib.sha256(event_name.encode("utf-8")).hexdigest()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event):
    """
    Create new event
    """
    event_id = convert_to_event_id(event.event_name)
    if event_id in events:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict: event exists")

    event_data = event.model_dump(exclude_unset=True)
    events[event_id] = event_data
    return {"event_id": event_id, **event_data}

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """
    Delete an event
    """
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found: Event doesn't exist")

    del events[event_id]

@router.patch("/{event_id}", status_code=status.HTTP_200_OK)
async def update_event(event_id: str, event: EventUpdate):
    """
    Partial update of an event. Only provided fields will be modified.
    """
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found: Event doesn't exist")

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
    return {"event_id": event_id, **current_event}

@router.get("", status_code=status.HTTP_200_OK)
async def get_all_events():
    """
    List all events
    """
    return [{"event_id": eid, **edata} for eid, edata in events.items()]

@router.get("/{event_id}", status_code=status.HTTP_200_OK)
async def get_event(event_id: str):
    if event_id not in events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found: Event doesn't exist")

    return {"event_id": event_id, **events[event_id]}