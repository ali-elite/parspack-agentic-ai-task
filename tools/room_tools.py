from typing import Optional
from pydantic import BaseModel
from agents import function_tool
from utils.db import HOTEL_ROOMS


class RoomAvailability(BaseModel):
    room_type: str
    available_count: int
    message: str
    success: bool


class RoomBooking(BaseModel):
    room_id: str
    room_type: str
    nights: int
    total_cost: float
    message: str
    success: bool


@function_tool
def check_room_availability(room_type: str) -> RoomAvailability:
    """
    Checks the availability of a specific type of room.
    
    Args:
        room_type: The type of room to check (e.g., 'single', 'double', 'triple').
    """
    available_rooms = [room for room in HOTEL_ROOMS if room['type'] == room_type and room['available']]
    count = len(available_rooms)
    
    if count == 0:
        return RoomAvailability(
            room_type=room_type,
            available_count=0,
            message=f"Sorry, no {room_type} rooms are available.",
            success=False
        )
    
    return RoomAvailability(
        room_type=room_type,
        available_count=count,
        message=f"There are {count} {room_type} rooms available.",
        success=True
    )


@function_tool
def book_room(room_type: str, nights: int) -> RoomBooking:
    """
    Books a room for a specified number of nights.

    Args:
        room_type: The type of room to book.
        nights: The number of nights to book the room for.
    """
    available_rooms = [room for room in HOTEL_ROOMS if room['type'] == room_type and room['available']]
    
    if not available_rooms:
        return RoomBooking(
            room_id="",
            room_type=room_type,
            nights=nights,
            total_cost=0.0,
            message=f"Sorry, no {room_type} rooms are available for booking.",
            success=False
        )
    
    room_to_book = available_rooms[0]
    room_to_book['available'] = False  # Mark the room as booked
    
    total_cost = room_to_book['price_per_night'] * nights
    
    return RoomBooking(
        room_id=room_to_book['id'],
        room_type=room_type,
        nights=nights,
        total_cost=total_cost,
        message=f"Successfully booked a {room_type} room ({room_to_book['id']}) for {nights} nights. Total cost: ${total_cost}.",
        success=True
    )