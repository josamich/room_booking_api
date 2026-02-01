from fastapi import APIRouter
from .rooms import router as rooms_router
from .bookings import router as bookings_router

api_router = APIRouter()
api_router.include_router(rooms_router)
api_router.include_router(bookings_router)

__all__ = ["api_router"]
