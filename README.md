# Room Booking API

A Simple REST API for managing meeting room bookings built with FastAPI. Implemented with help of AIs (GPT-5, Claude Sonnet 4).

## Features

- **Room Management**: Create, view, and manage meeting rooms with details like capacity and description
- **Room Booking Management**: Create, view, and cancel meeting room bookings
- **Conflict Detection**: Automatically prevents overlapping bookings
- **Free Slot Discovery**: Find available time slots for meetings
- **Real-time Validation**: Prevents booking in the past and validates room existence
- **In-memory Storage**: Fast, lightweight data storage for development

## Quick Start

### Prerequisites

- Docker (recommended)
- Or Python 3.11+ with pip

### Running with Docker

```bash
# Build the image
docker build -t room_booking_api .

# Run the container
docker run -p 8000:8000 room_booking_api
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Room Management

### 1. List All Rooms

**GET** `/rooms`

Get all available rooms in the system.

**Response:**
```json
{
  "room_id": "conference-room-1",
  "name": "Main Conference Room",
  "capacity": 12,
  "description": "Large conference room with projector"
}
```

### 2. Get Room Details

**GET** `/rooms/{room_id}`

Get details of a specific room.

**Response:**
```json
{
  "room_id": "conference-room-1",
  "name": "Main Conference Room",
  "capacity": 12,
  "description": "Large conference room with projector"
}
```

**Error Codes:**
- `404`: Room not found

### 3. Create Room

**POST** `/rooms`

Create a new room. The room ID is automatically generated.

**Request:**
```json
{
  "name": "Training Room",
  "capacity": 20,
  "description": "Large training room with whiteboards"
}
```

**Response:**
```json
{
  "room_id": "room-a1b2c3d4",
  "name": "Training Room",
  "capacity": 20,
  "description": "Large training room with whiteboards"
}
```

### 4. Delete Room

**DELETE** `/rooms/{room_id}`

Delete a room (only if no active bookings exist).

**Response:**
```json
{
  "status": "deleted",
  "room_id": "room-a1b2c3d4"
}
```

**Error Codes:**
- `400`: Cannot delete room with existing bookings
- `404`: Room not found

### Booking Management

### 5. Create Booking

**POST** `/book`

Create a new room booking. The booking ID is automatically generated.

**Request:**
```json
{
  "room_id": "conference-room-1",
  "start": "2026-02-03T09:00:00",
  "end": "2026-02-03T10:00:00"
}
```

**Response:**
```json
{
  "booking_id": "30586249-7441-4374-a9b3-8881e0eefa26",
  "room_id": "conference-room-1",
  "start": "2026-02-03T09:00:00",
  "end": "2026-02-03T10:00:00"
}
```

**Error Codes:**
- `400`: Invalid time range or booking in the past
- `404`: Room not found
- `409`: Time slot conflicts with existing booking
- `422`: Wrong format

### 6. List All Bookings

**GET** `/bookings`

Get all bookings across all rooms, sorted by start time.

**Response:**
```json
[
  {
    "booking_id": "123e4567-e89b-12d3-a456-426614174000",
    "room_id": "conference-room-1",
    "start": "2026-02-03T09:00:00",
    "end": "2026-02-03T10:00:00"
  },
  {
    "booking_id": "456e7890-e89b-12d3-a456-426614174001",
    "room_id": "meeting-room-2",
    "start": "2026-02-03T11:00:00",
    "end": "2026-02-03T12:00:00"
  }
]
```

### 7. List Bookings by Room

**GET** `/bookings/{room_id}`

Get all bookings for a specific room.

**Response:**
```json
[
  {
    "booking_id": "123e4567-e89b-12d3-a456-426614174000",
    "room_id": "conference-room-1",
    "start": "2026-02-03T09:00:00",
    "end": "2026-02-03T10:00:00"
  }
]
```

**Error Codes:**
- `404`: Room not found

### 8. Cancel Booking

**DELETE** `/cancel`

Cancel an existing booking. You need both the room ID and the booking ID to cancel.

**Request:**
```json
{
  "room_id": "conference-room-1",
  "booking_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**
```json
{
  "status": "deleted"
}
```

**Error Codes:**
- `404`: Room not found or booking not found

### 9. Find Free Slots

**GET** `/free_slots/{room_id}?from_time={datetime}&to_time={datetime}&duration_min={minutes}`

Find available time slots in a room within a time range.

**Parameters:**
- `room_id`: Room identifier
- `from_time`: Start of search period (ISO 8601 datetime)
- `to_time`: End of search period (ISO 8601 datetime)
- `duration_min`: Minimum slot duration in minutes (default: 30)

**Example:**
```
GET /free_slots/conference-room-1?from_time=2026-02-03T08:00:00&to_time=2026-02-03T18:00:00&duration_min=60
```

**Response:**
```json
[
  {
    "start": "2026-02-03T08:00:00",
    "end": "2026-02-03T09:00:00"
  },
  {
    "start": "2026-02-03T10:00:00",
    "end": "2026-02-03T18:00:00"
  }
]
```

**Error Codes:**
- `404`: Room not found

## Predefined Rooms

The system comes with three predefined rooms:

- **conference-room-1**: Main Conference Room (12 people) - Large conference room with projector
- **meeting-room-2**: Small Meeting Room (6 people) - Cozy meeting space for small teams  
- **boardroom-3**: Executive Boardroom (8 people) - Executive boardroom with video conferencing

## Data Models

### Room
```json
{
  "room_id": "string (auto-generated)",
  "name": "string",
  "capacity": "integer (optional)",
  "description": "string (optional)"
}
```

### RoomRequest
```json
{
  "name": "string",
  "capacity": "integer (optional)",
  "description": "string (optional)"
}
```

### BookingRequest
```json
{
  "room_id": "string",
  "start": "datetime (ISO 8601)",
  "end": "datetime (ISO 8601)"
}
```

### BookingResponse
```json
{
  "booking_id": "string (UUID, auto-generated)",
  "room_id": "string",
  "start": "datetime (ISO 8601)",
  "end": "datetime (ISO 8601)"
}
```

### CancelRequest
```json
{
  "room_id": "string",
  "booking_id": "string (UUID)"
}
```

## Example Usage

### Using curl

```bash
# List all available rooms
curl "http://localhost:8000/rooms"

# Get details of a specific room
curl "http://localhost:8000/rooms/conference-room-1"

# Create a new room
curl -X POST "http://localhost:8000/rooms" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Training Room",
    "capacity": 20,
    "description": "Large training room with whiteboards"
  }'

# Create a booking (booking_id is auto-generated)
curl -X POST "http://localhost:8000/book" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "conference-room-1",
    "start": "2026-02-03T09:00:00",
    "end": "2026-02-03T10:00:00"
  }'

# List all bookings across all rooms
curl "http://localhost:8000/bookings"

# List all bookings for a specific room
curl "http://localhost:8000/bookings/conference-room-1"

# Find free slots
curl "http://localhost:8000/free_slots/conference-room-1?from_time=2026-02-03T08:00:00&to_time=2026-02-03T18:00:00&duration_min=60"

# Cancel a booking (use the booking_id from the create response)
curl -X DELETE "http://localhost:8000/cancel" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "conference-room-1",
    "booking_id": "30586249-7441-4374-a9b3-8881e0eefa26"
  }'

# Delete a room (only if no bookings exist)
curl -X DELETE "http://localhost:8000/rooms/room-a1b2c3d4"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# List all rooms
response = requests.get(f"{base_url}/rooms")
rooms = response.json()
print(f"Available rooms: {len(rooms)}")

# Create a new room
room_data = {
    "name": "Training Room",
    "capacity": 20,
    "description": "Large training room with whiteboards"
}
response = requests.post(f"{base_url}/rooms", json=room_data)
new_room = response.json()
print(f"Created room: {new_room['room_id']}")

# Create a booking (booking_id is auto-generated)
booking_data = {
    "room_id": "conference-room-1",
    "start": "2026-02-03T09:00:00",
    "end": "2026-02-03T10:00:00"
}
response = requests.post(f"{base_url}/book", json=booking_data)
booking = response.json()
print(f"Created booking: {booking['booking_id']}")

# List all bookings across all rooms
response = requests.get(f"{base_url}/bookings")
all_bookings = response.json()
print(f"Found {len(all_bookings)} total bookings")

# Cancel the booking using the returned booking_id
cancel_data = {
    "room_id": booking["room_id"],
    "booking_id": booking["booking_id"]
}
response = requests.delete(f"{base_url}/cancel", json=cancel_data)
print(f"Cancelled booking: {response.json()}")
```

## Architecture

The API uses an efficient in-memory data structure for fast operations:

- **Room Management**: Predefined rooms with CRUD operations and validation
- **Sorted List**: Bookings are stored in chronological order using binary search for O(log n) conflict detection
- **ID Mapping**: Direct lookup by booking ID for O(1) cancellation
- **Room Isolation**: Each room maintains its own booking data structure
- **Validation**: All booking operations validate room existence first

## Development

### Project Structure

```
.
├── main.py              # FastAPI application and endpoints
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore patterns
└── README.md           # This documentation
```

### Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI web server implementation
- **Pydantic**: Data validation using Python type annotations

### Running Tests

```bash
# Install test dependencies (add to requirements.txt if needed)
pip install pytest httpx

# Run tests
pytest
```

## Limitations

- **In-Memory Storage**: Data is lost when the application restarts
- **Single Instance**: Not suitable for multi-instance deployments without external storage
- **No Authentication**: Currently no user authentication or authorization

## Future Enhancements

- [ ] Persistent database storage (PostgreSQL/SQLite)
- [ ] User authentication and authorization
- [ ] Room capacity and resource management
- [ ] Email notifications for bookings
- [ ] Recurring booking patterns
- [ ] Booking modification (not just cancel/rebook)
- [ ] API rate limiting
- [ ] Comprehensive test suite

## License

This project is currently in development. License information will be added soon.

## Contributing

This project is currently in development. Contribution guidelines will be established as the project matures.