from datetime import datetime, timedelta
from typing import List
import bisect
import uuid
from fastapi import HTTPException
from app.models import BookingRequest, BookingResponse
from app.services.room_service import RoomService, ROOMS


# In-memory store: room_id -> {"sorted": [(start, end, booking_id)], "by_id": {booking_id:(start, end)}}
bookings = {}


class BookingService:
    @staticmethod
    def get_room_data(room_id: str):
        """Get or initialize booking data for a room"""
        if room_id not in bookings:
            bookings[room_id] = {"sorted": [], "by_id": {}}
        return bookings[room_id]
    
    @staticmethod
    def can_book(sorted_list, start, end):
        """Check if a time slot is available"""
        i = bisect.bisect_left(sorted_list, (start, end, ""))
        if i > 0 and sorted_list[i-1][1] > start:
            return False
        if i < len(sorted_list) and sorted_list[i][0] < end:
            return False
        return True
    
    @staticmethod
    def create_booking(req: BookingRequest):
        """Create a new room booking"""
        RoomService.validate_room_exists(req.room_id)
        
        now = datetime.utcnow()
        if req.start >= req.end:
            raise HTTPException(400, "Start must be before end")
        if req.start < now:
            raise HTTPException(400, "Cannot book in the past")

        room = BookingService.get_room_data(req.room_id)
        sorted_list = room["sorted"]

        if not BookingService.can_book(sorted_list, req.start, req.end):
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
    
    @staticmethod
    def list_all_bookings() -> List[BookingResponse]:
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
    
    @staticmethod
    def list_room_bookings(room_id: str) -> List[BookingResponse]:
        """Get all bookings for a specific room"""
        RoomService.validate_room_exists(room_id)
        room = BookingService.get_room_data(room_id)
        return [
            BookingResponse(
                booking_id=b_id,
                room_id=room_id,
                start=s,
                end=e
            )
            for (s, e, b_id) in room["sorted"]
        ]
    
    @staticmethod
    def cancel_booking(room_id: str, booking_id: str):
        """Cancel an existing booking"""
        RoomService.validate_room_exists(room_id)
        
        room = BookingService.get_room_data(room_id)
        if booking_id not in room["by_id"]:
            raise HTTPException(404, "Booking not found")

        start, end = room["by_id"].pop(booking_id)
        room["sorted"].remove((start, end, booking_id))
        return {"status": "deleted"}
    
    @staticmethod
    def find_free_slots(room_id: str, from_time: datetime, to_time: datetime, duration_min: int = 30):
        """Find available time slots in a room"""
        RoomService.validate_room_exists(room_id)
        
        room = BookingService.get_room_data(room_id)
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
