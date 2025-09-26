from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from agents import function_tool
from utils.db import RESTAURANT_TABLES, TABLE_RESERVATIONS


class RestaurantTable(BaseModel):
    table_number: int
    capacity: int
    location: str
    available: bool
    reserved_by: Optional[str] = None
    reserved_date: Optional[str] = None
    reserved_time: Optional[str] = None
    reservation_duration: Optional[int] = None


class TableAvailability(BaseModel):
    capacity: int
    available_count: int
    available_tables: List[int]
    message: str
    success: bool


class TableReservation(BaseModel):
    reservation_id: str
    table_number: int
    capacity: int
    location: str
    customer_name: str
    party_size: int
    reserved_date: str
    reserved_time: str
    duration_hours: int
    special_requests: Optional[str] = None
    status: str = "confirmed"
    created_at: str
    message: str
    success: bool


class TableReservationsList(BaseModel):
    reservations: List[Dict[str, Any]]
    count: int
    message: str
    success: bool


@function_tool
def check_table_availability(party_size: int, preferred_date: str = None, preferred_time: str = None) -> TableAvailability:
    """
    Check availability of tables for a specific party size.
    
    Args:
        party_size: Number of people in the party
        preferred_date: Preferred date in YYYY-MM-DD format (optional)
        preferred_time: Preferred time in HH:MM format (optional)
    """
    # Find tables that can accommodate the party size
    suitable_tables = [
        table for table in RESTAURANT_TABLES 
        if table['capacity'] >= party_size and table['available']
    ]
    
    if not suitable_tables:
        return TableAvailability(
            capacity=party_size,
            available_count=0,
            available_tables=[],
            message=f"Sorry, no tables available for {party_size} people.",
            success=False
        )
    
    # Get table numbers
    available_table_numbers = [table['table_number'] for table in suitable_tables]
    
    # Group by capacity for better info
    capacity_info = {}
    for table in suitable_tables:
        cap = table['capacity']
        if cap not in capacity_info:
            capacity_info[cap] = []
        capacity_info[cap].append(table['table_number'])
    
    # Create detailed message
    capacity_details = []
    for capacity, tables in capacity_info.items():
        capacity_details.append(f"{len(tables)} tables for {capacity} people (Tables: {', '.join(map(str, tables))})")
    
    message = f"Available tables for {party_size}+ people:\n" + "\n".join(capacity_details)
    
    return TableAvailability(
        capacity=party_size,
        available_count=len(suitable_tables),
        available_tables=available_table_numbers,
        message=message,
        success=True
    )


@function_tool
def reserve_table(customer_name: str, party_size: int, reserved_date: str, reserved_time: str, 
                  duration_hours: int = 2, table_preference: int = None, 
                  special_requests: str = None) -> TableReservation:
    """
    Reserve a table for dining.
    
    Args:
        customer_name: Name of the customer making the reservation
        party_size: Number of people in the party
        reserved_date: Date for reservation (YYYY-MM-DD format)
        reserved_time: Time for reservation (HH:MM format)
        duration_hours: Duration of reservation in hours (default 2)
        table_preference: Preferred table number (optional)
        special_requests: Any special requests (optional)
    """
    # Check if specific table is requested and available
    if table_preference:
        preferred_table = next(
            (table for table in RESTAURANT_TABLES 
             if table['table_number'] == table_preference), None
        )
        
        if preferred_table:
            if preferred_table['capacity'] >= party_size and preferred_table['available']:
                # Reserve the preferred table
                preferred_table['available'] = False
                preferred_table['reserved_by'] = customer_name
                preferred_table['reserved_date'] = reserved_date
                preferred_table['reserved_time'] = reserved_time
                preferred_table['reservation_duration'] = duration_hours
                
                # Generate reservation ID
                reservation_id = f"TBL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{table_preference:02d}"
                
                # Add to reservations list
                reservation_record = {
                    "reservation_id": reservation_id,
                    "table_number": table_preference,
                    "customer_name": customer_name,
                    "party_size": party_size,
                    "reserved_date": reserved_date,
                    "reserved_time": reserved_time,
                    "duration_hours": duration_hours,
                    "special_requests": special_requests,
                    "status": "confirmed",
                    "created_at": datetime.now().isoformat()
                }
                TABLE_RESERVATIONS.append(reservation_record)
                
                return TableReservation(
                    reservation_id=reservation_id,
                    table_number=table_preference,
                    capacity=preferred_table['capacity'],
                    location=preferred_table['location'],
                    customer_name=customer_name,
                    party_size=party_size,
                    reserved_date=reserved_date,
                    reserved_time=reserved_time,
                    duration_hours=duration_hours,
                    special_requests=special_requests,
                    status="confirmed",
                    created_at=datetime.now().isoformat(),
                    message=f"✅ Table {table_preference} reserved successfully for {customer_name} on {reserved_date} at {reserved_time} for {party_size} people.",
                    success=True
                )
            else:
                return TableReservation(
                    reservation_id="",
                    table_number=0,
                    capacity=0,
                    location="",
                    customer_name=customer_name,
                    party_size=party_size,
                    reserved_date=reserved_date,
                    reserved_time=reserved_time,
                    duration_hours=duration_hours,
                    message=f"❌ Table {table_preference} is not available or too small for {party_size} people.",
                    success=False,
                    created_at=datetime.now().isoformat()
                )
        else:
            return TableReservation(
                reservation_id="",
                table_number=0,
                capacity=0,
                location="",
                customer_name=customer_name,
                party_size=party_size,
                reserved_date=reserved_date,
                reserved_time=reserved_time,
                duration_hours=duration_hours,
                message=f"❌ Table {table_preference} does not exist.",
                success=False,
                created_at=datetime.now().isoformat()
            )
    
    # Find the best available table automatically
    suitable_tables = [
        table for table in RESTAURANT_TABLES 
        if table['capacity'] >= party_size and table['available']
    ]
    
    if not suitable_tables:
        return TableReservation(
            reservation_id="",
            table_number=0,
            capacity=0,
            location="",
            customer_name=customer_name,
            party_size=party_size,
            reserved_date=reserved_date,
            reserved_time=reserved_time,
            duration_hours=duration_hours,
            message=f"❌ No tables available for {party_size} people on {reserved_date} at {reserved_time}.",
            success=False,
            created_at=datetime.now().isoformat()
        )
    
    # Select the best table (smallest capacity that fits the party)
    best_table = min(suitable_tables, key=lambda x: x['capacity'])
    
    # Reserve the table
    best_table['available'] = False
    best_table['reserved_by'] = customer_name
    best_table['reserved_date'] = reserved_date
    best_table['reserved_time'] = reserved_time
    best_table['reservation_duration'] = duration_hours
    
    # Generate reservation ID
    reservation_id = f"TBL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{best_table['table_number']:02d}"
    
    # Add to reservations list
    reservation_record = {
        "reservation_id": reservation_id,
        "table_number": best_table['table_number'],
        "customer_name": customer_name,
        "party_size": party_size,
        "reserved_date": reserved_date,
        "reserved_time": reserved_time,
        "duration_hours": duration_hours,
        "special_requests": special_requests,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    TABLE_RESERVATIONS.append(reservation_record)
    
    return TableReservation(
        reservation_id=reservation_id,
        table_number=best_table['table_number'],
        capacity=best_table['capacity'],
        location=best_table['location'],
        customer_name=customer_name,
        party_size=party_size,
        reserved_date=reserved_date,
        reserved_time=reserved_time,
        duration_hours=duration_hours,
        special_requests=special_requests,
        status="confirmed",
        created_at=datetime.now().isoformat(),
        message=f"✅ Table {best_table['table_number']} ({best_table['location']}) reserved successfully for {customer_name} on {reserved_date} at {reserved_time} for {party_size} people. Reservation ID: {reservation_id}",
        success=True
    )


@function_tool
def get_table_reservations(customer_name: str = None, date: str = None, table_number: int = None) -> TableReservationsList:
    """
    Get table reservations based on filters.
    
    Args:
        customer_name: Filter by customer name
        date: Filter by date (YYYY-MM-DD)
        table_number: Filter by table number
    """
    filtered_reservations = []
    
    for reservation in TABLE_RESERVATIONS:
        include = True
        
        if customer_name and reservation.get('customer_name', '').lower() != customer_name.lower():
            include = False
        if date and reservation.get('reserved_date') != date:
            include = False
        if table_number and reservation.get('table_number') != table_number:
            include = False
            
        if include:
            filtered_reservations.append(reservation)
    
    return TableReservationsList(
        reservations=filtered_reservations,
        count=len(filtered_reservations),
        message=f"Found {len(filtered_reservations)} table reservations",
        success=True
    )


@function_tool
def cancel_table_reservation(reservation_id: str) -> Dict[str, Any]:
    """
    Cancel a table reservation and free up the table.
    
    Args:
        reservation_id: The reservation ID to cancel
    """
    reservation_index = None
    reservation_data = None
    
    for i, reservation in enumerate(TABLE_RESERVATIONS):
        if reservation['reservation_id'] == reservation_id:
            reservation_index = i
            reservation_data = reservation
            break
    
    if reservation_index is None:
        return {
            "message": f"Reservation {reservation_id} not found",
            "success": False
        }
    
    # Free up the table
    table_number = reservation_data['table_number']
    table = next((t for t in RESTAURANT_TABLES if t['table_number'] == table_number), None)
    
    if table:
        table['available'] = True
        table['reserved_by'] = None
        table['reserved_date'] = None
        table['reserved_time'] = None
        table['reservation_duration'] = None
    
    # Remove reservation
    TABLE_RESERVATIONS.pop(reservation_index)
    
    return {
        "reservation_id": reservation_id,
        "table_number": table_number,
        "message": f"✅ Table reservation {reservation_id} cancelled successfully. Table {table_number} is now available.",
        "success": True
    }


@function_tool
def get_all_tables_status() -> Dict[str, Any]:
    """
    Get the status of all restaurant tables.
    """
    tables_by_capacity = {}
    
    for table in RESTAURANT_TABLES:
        capacity = table['capacity']
        if capacity not in tables_by_capacity:
            tables_by_capacity[capacity] = {
                'available': [],
                'reserved': []
            }
        
        if table['available']:
            tables_by_capacity[capacity]['available'].append({
                'table_number': table['table_number'],
                'location': table['location']
            })
        else:
            tables_by_capacity[capacity]['reserved'].append({
                'table_number': table['table_number'],
                'location': table['location'],
                'reserved_by': table['reserved_by'],
                'reserved_date': table['reserved_date'],
                'reserved_time': table['reserved_time']
            })
    
    # Create summary
    summary = []
    total_available = 0
    total_reserved = 0
    
    for capacity in sorted(tables_by_capacity.keys()):
        data = tables_by_capacity[capacity]
        available_count = len(data['available'])
        reserved_count = len(data['reserved'])
        total_available += available_count
        total_reserved += reserved_count
        
        summary.append(f"{capacity}-person tables: {available_count} available, {reserved_count} reserved")
    
    return {
        "tables_by_capacity": tables_by_capacity,
        "summary": summary,
        "total_available": total_available,
        "total_reserved": total_reserved,
        "message": f"Restaurant has {total_available} available tables and {total_reserved} reserved tables",
        "success": True
    }
