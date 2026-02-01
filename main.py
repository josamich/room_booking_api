from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import bisect
import uuid

app = FastAPI(title="Meeting Room Booking API")

# Room management
class Room(BaseModel):
    room_id: str
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None

class RoomRequest(BaseModel):
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None

# Predefined rooms - in real app, this would come from database
ROOMS: Dict[str, Room] = {
    "conference-room-1": Room(
        room_id="conference-room-1",
        name="Main Conference Room",
        capacity=12,
        description="Large conference room with projector"
    ),
    "meeting-room-2": Room(
        room_id="meeting-room-2", 
        name="Small Meeting Room",
        capacity=6,
        description="Cozy meeting space for small teams"
    ),
    "boardroom-3": Room(
        room_id="boardroom-3",
        name="Executive Boardroom",
        capacity=8,
        description="Executive boardroom with video conferencing"
    )
}

# In-memory store: room_id -> {"sorted": [(start, end, booking_id)], "by_id": {booking_id:(start, end)}}
bookings = {}

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

# Helpers

def get_room_data(room_id: str):
    if room_id not in bookings:
        bookings[room_id] = {"sorted": [], "by_id": {}}
    return bookings[room_id]

def can_book(sorted_list, start, end):
    i = bisect.bisect_left(sorted_list, (start, end, ""))
    if i > 0 and sorted_list[i-1][1] > start:
        return False
    if i < len(sorted_list) and sorted_list[i][0] < end:
        return False
    return True

def validate_room_exists(room_id: str):
    if room_id not in ROOMS:
        raise HTTPException(404, f"Room '{room_id}' not found")

# Room Management Endpoints

@app.get("/rooms", response_model=List[Room])
def list_rooms():
    """Get all available rooms"""
    return list(ROOMS.values())

@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: str):
    """Get details of a specific room"""
    validate_room_exists(room_id)
    return ROOMS[room_id]

@app.post("/rooms", response_model=Room)
def create_room(room_req: RoomRequest):
    """Create a new room"""
    room_id = f"room-{str(uuid.uuid4())[:8]}"
    room = Room(
        room_id=room_id,
        name=room_req.name,
        capacity=room_req.capacity,
        description=room_req.description
    )
    ROOMS[room_id] = room
    return room

@app.delete("/rooms/{room_id}")
def delete_room(room_id: str):
    """Delete a room (only if no bookings exist)"""
    validate_room_exists(room_id)
    
    # Check if room has any bookings
    if room_id in bookings and bookings[room_id]["sorted"]:
        raise HTTPException(400, "Cannot delete room with existing bookings")
    
    del ROOMS[room_id]
    if room_id in bookings:
        del bookings[room_id]
    
    return {"status": "deleted", "room_id": room_id}

# Booking Endpoints

@app.post("/book", response_model=BookingResponse)
def create_booking(req: BookingRequest):
    """Create a new room booking"""
    validate_room_exists(req.room_id)
    
    now = datetime.utcnow()
    if req.start >= req.end:
        raise HTTPException(400, "Start must be before end")
    if req.start < now:
        raise HTTPException(400, "Cannot book in the past")

    room = get_room_data(req.room_id)
    sorted_list = room["sorted"]

    if not can_book(sorted_list, req.start, req.end):
        raise HTTPException(409, "Time slot overlaps with existing booking")

    booking_id = str(uuid.uuid4())
    entry = (req.start, req.end, booking_id)

    i = bisect.bisect_left(sorted_list, entry)
    sorted_list.insert(i, entry)
    room["by_id"][booking_id] = (req.start, req.end)

    return BookingResponse(
        booking_id=booking_id,
        room_id=req.room_id,
        start=req.start,
        end=req.end
    )

@app.get("/bookings", response_model=List[BookingResponse])
def list_all_bookings():
    """Get all bookings across all rooms, sorted by start time"""
    all_bookings = []
    
    for room_id, room_data in bookings.items():
        # Only include bookings for rooms that still exist
        if room_id in ROOMS:
            for (start, end, booking_id) in room_data["sorted"]:
                all_bookings.append(BookingResponse(
                    booking_id=booking_id,
                    room_id=room_id,
                    start=start,
                    end=end
                ))
    
    # Sort by start time across all rooms
    all_bookings.sort(key=lambda x: x.start)
    return all_bookings

@app.get("/bookings/{room_id}", response_model=List[BookingResponse])
def list_bookings(room_id: str):
    """Get all bookings for a specific room"""
    validate_room_exists(room_id)
    room = get_room_data(room_id)
    return [
        BookingResponse(
            booking_id=b_id,
            room_id=room_id,
            start=s,
            end=e
        )
        for (s, e, b_id) in room["sorted"]
    ]

@app.delete("/cancel", response_model=dict)
def cancel_booking(req: CancelRequest):
    """Cancel an existing booking"""
    validate_room_exists(req.room_id)
    
    room = get_room_data(req.room_id)
    if req.booking_id not in room["by_id"]:
        raise HTTPException(404, "Booking not found")

    start, end = room["by_id"].pop(req.booking_id)
    room["sorted"].remove((start, end, req.booking_id))
    return {"status": "deleted"}

@app.get("/free_slots/{room_id}")
def free_slots(
    room_id: str,
    from_time: datetime,
    to_time: datetime,
    duration_min: int = 30
):
    """Find available time slots in a room"""
    validate_room_exists(room_id)
    
    room = get_room_data(room_id)
    sorted_list = room["sorted"]
    slots = []
    current = from_time
    duration = timedelta(minutes=duration_min)

    for (s, e, _) in sorted_list:
        if s - current >= duration:
            slots.append({"start": current, "end": s})
        current = max(current, e)

    if to_time - current >= duration:
        slots.append({"start": current, "end": to_time})

    return slots

