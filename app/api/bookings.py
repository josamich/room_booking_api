from fastapi import APIRouter
from datetime import datetime
from typing import List
from app.models import BookingRequest, BookingResponse, CancelRequest
from app.services import BookingService

router = APIRouter(tags=["bookings"])


@router.post("/book", response_model=BookingResponse)
def create_booking(req: BookingRequest):
    """Create a new room booking"""
    return BookingService.create_booking(req)


@router.get("/bookings", response_model=List[BookingResponse])
def list_all_bookings():
    """Get all bookings across all rooms, sorted by start time"""
    return BookingService.list_all_bookings()


@router.get("/bookings/{room_id}", response_model=List[BookingResponse])
def list_bookings(room_id: str):
    """Get all bookings for a specific room"""
    return BookingService.list_room_bookings(room_id)


@router.delete("/cancel")
def cancel_booking(req: CancelRequest):
    """Cancel an existing booking"""
    return BookingService.cancel_booking(req.room_id, req.booking_id)


@router.get("/free_slots/{room_id}")
def free_slots(
    room_id: str,
    from_time: datetime,
    to_time: datetime,
    duration_min: int = 30
):
    """Find available time slots in a room"""
    return BookingService.find_free_slots(room_id, from_time, to_time, duration_min)
