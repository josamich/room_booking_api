from pydantic import BaseModel
from datetime import datetime


class BookingRequest(BaseModel):
    room_id: str
    start: datetime
    end: datetime


class CancelRequest(BaseModel):
    room_id: str
    booking_id: str


class BookingResponse(BaseModel):
    booking_id: str
    room_id: str
    start: datetime
    end: datetime
