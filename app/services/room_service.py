from typing import Dict
import uuid
from fastapi import HTTPException
from app.models import Room, RoomRequest


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


class RoomService:
    @staticmethod
    def get_all_rooms():
        """Get all available rooms"""
        return list(ROOMS.values())
    
    @staticmethod
    def get_room(room_id: str):
        """Get a specific room by ID"""
        if room_id not in ROOMS:
            raise HTTPException(404, f"Room '{room_id}' not found")
        return ROOMS[room_id]
    
    @staticmethod
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
    
    @staticmethod
    def delete_room(room_id: str, bookings_store):
        """Delete a room (only if no bookings exist)"""
        if room_id not in ROOMS:
            raise HTTPException(404, f"Room '{room_id}' not found")
        
        # Check if room has any bookings
        if room_id in bookings_store and bookings_store[room_id]["sorted"]:
            raise HTTPException(400, "Cannot delete room with existing bookings")
        
        del ROOMS[room_id]
        if room_id in bookings_store:
            del bookings_store[room_id]
        
        return {"status": "deleted", "room_id": room_id}
    
    @staticmethod
    def validate_room_exists(room_id: str):
        """Validate that a room exists"""
        if room_id not in ROOMS:
            raise HTTPException(404, f"Room '{room_id}' not found")
