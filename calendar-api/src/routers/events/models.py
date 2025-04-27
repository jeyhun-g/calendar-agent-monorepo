from pydantic import BaseModel
from typing import Optional

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