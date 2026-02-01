from fastapi import FastAPI
from app.api import api_router

app = FastAPI(
    title="Meeting Room Booking API",
    description="API for managing meeting room bookings",
    version="1.0.0"
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Meeting Room Booking API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
