from pydantic import BaseModel
from typing import Optional


class Room(BaseModel):
    room_id: str
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None


class RoomRequest(BaseModel):
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None
