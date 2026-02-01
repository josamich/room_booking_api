from fastapi import APIRouter
from typing import List
from app.models import Room, RoomRequest
from app.services import RoomService, bookings

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=List[Room])
def list_rooms():
    """Get all available rooms"""
    return RoomService.get_all_rooms()


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: str):
    """Get details of a specific room"""
    return RoomService.get_room(room_id)


@router.post("", response_model=Room)
def create_room(room_req: RoomRequest):
    """Create a new room"""
    return RoomService.create_room(room_req)


@router.delete("/{room_id}")
def delete_room(room_id: str):
    """Delete a room (only if no bookings exist)"""
    return RoomService.delete_room(room_id, bookings)
