## ChatGPT (GPT-5)
Mitä frameworkiä suosittelet: Tehtäväsi on toteuttaa yksinkertainen kokoushuoneiden varausrajapinta (API).
Palvelun tulee tarjota käyttäjille seuraavat toiminnot:
● Varauksen luonti: Varaa huone tietylle aikavälille.
● Varauksen peruutus: Poista varaus.
● Varausten katselu: Listaa kaikki tietyn huoneen varaukset.
Toimintalogiikka (business rules):
● Varaukset eivät saa mennä päällekkäin (kaksi henkilöä ei voi varata samaa huonetta samaan aikaan).
● Varaukset eivät voi sijoittua menneisyyteen.
● Aloitusajan täytyy olla ennen lopetusaikaa. Eniten mietityttää vapaana olevan slotin etsiminen.

Tämä on erinomainen tehtävä API-frameworkin valinnalle — ja valinta riippuu siitä, mitä **vaatimuksia** ja **prioriteetteja** sinulla on:

## 🥇 Suosittelen: **FastAPI**

**FastAPI** on tällä hetkellä yksi parhaista valinnoista, kun:

✅ Haluat **nopeasti kehitettävän** REST API:n
✅ Haluat automaattisesti generoituvaa **dokumentaatiota (OpenAPI / Swagger)**
✅ Haluat **async-tuen** ilman monimutkaisuutta
✅ Haluat että pyyntöjä voi testata helposti selaimella

👉 FastAPI yhdistettynä Pydantic-malliin tekee validoinnista helppoa.

---

## Vaihtoehdot

| Framework        | Milloin käyttää                                                  |
| ---------------- | ---------------------------------------------------------------- |
| **Flask**        | Jos haluat mahdollisimman yksinkertaisen ja tutun                |
| **Django + DRF** | Jos projekti kasvaa muihin web-toimintoihin                      |
| **Starlette**    | Jos haluat vähimmän mahdollisen rungon (FastAPI pohjautuu tähän) |

Aloitetaan **FastAPI-tyylillä**, koska se on nykyään kultastandardi pieniin API-palveluihin Pythonissa.

---

## 🛠 Pieni varaus API-luokka FastAPIlla

Alla on valmis esimerkki, joka sisältää:

✅ Varausten tallennuksen in-memory
✅ Päällekkäisyyksien eston
✅ Varausten listauksen eri huoneille
✅ Varauksen peruutuksen
✅ Vapaan slotin hakemisen annetulle aikavälille

### 📦 `main.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional
import bisect
import uuid

app = FastAPI(title="Meeting Room Booking API")

# In-memory store: huone -> {"sorted": [(start, end, id)], "by_id": {id:(start, end)}}
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

# Endpoints

@app.post("/book", response_model=BookingResponse)
def create_booking(req: BookingRequest):
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

@app.get("/bookings/{room_id}", response_model=List[BookingResponse])
def list_bookings(room_id: str):
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
```

---

## 🚀 Käyttöönotto

1. Asenna riippuvuudet:

```sh
pip install fastapi uvicorn
```

2. Käynnistä palvelin:

```sh
uvicorn main:app --reload
```

3. Mene selaimeen:
   ➡ [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

… ja kokeile API:a interaktiivisesti!

---

## 📌 Miksi FastAPI tässä on hyvä valinta?

✨ Moderni Python-tyyli (type hints + Pydantic)
✨ Dokumentaatio autogeneraattori
✨ Luonnollinen async-tuki
✨ Nopea kehitysaika

---

Jos haluat:
✔ lisätä autentikoinnin
✔ tallennuksen tietokantaan myöhemmin (SQLite/PostgreSQL)
✔ JWT-tokenit / käyttäjät

… niin voin kyllä jatkaa siitäkin!





## Claude Sonnet 4 (GitHub Copilot)

One thing is bothering me is that in real implementation we should have at first some fixed set (maybe possible to add and remove new rooms also) of rooms with unique ids also.

You're absolutely right! In a real implementation, we should have a predefined set of rooms with proper room management. Here's an improved version with room management:

```python
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
```

Key improvements:

1. Room Management:

- Predefined rooms with IDs, names, capacity, and descriptions
- CRUD operations for rooms
- Room validation before booking

2. Better Data Structure:
- Room model with proper attributes
- ROOMS dictionary for room management
- Room existence validation

3. New Endpoints:
- GET /rooms - List all rooms
- GET /rooms/{room_id} - Get room details
- POST /rooms - Create new room
- DELETE /rooms/{room_id} - - Delete room (if no bookings)

4. Enhanced Validation:
- Check room exists before booking
- Prevent deleting rooms with active bookings
- Better error messages



Generate docs

# Room Booking API

A Simple REST API for managing meeting room bookings built with FastAPI.

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
[
  {
    "room_id": "conference-room-1",
    "name": "Main Conference Room",
    "capacity": 12,
    "description": "Large conference room with projector"
  },
  {
    "room_id": "meeting-room-2",
    "name": "Small Meeting Room",
    "capacity": 6,
    "description": "Cozy meeting space for small teams"
  }
]
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