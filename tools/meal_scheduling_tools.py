from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from agents import function_tool
from utils.db import RESTAURANT_MENU, WEEKLY_MEAL_PROGRAM, FOOD_RESERVATIONS


class MealOfTheDay(BaseModel):
    meal_type: str  # breakfast, lunch, dinner
    name: str
    description: str
    available: bool
    price: float


class DayMealProgram(BaseModel):
    day: str
    date: str
    breakfast: MealOfTheDay
    lunch: MealOfTheDay
    dinner: MealOfTheDay
    message: str
    success: bool


class WeeklySchedule(BaseModel):
    week_start: str
    week_end: str
    daily_programs: List[DayMealProgram]
    message: str
    success: bool


class FoodReservation(BaseModel):
    reservation_id: str
    customer_name: Optional[str] = None
    room_number: Optional[int] = None
    food_item: str
    meal_type: str
    scheduled_date: str
    scheduled_time: str
    quantity: int
    total_price: float
    customizations: Optional[List[str]] = None
    special_instructions: Optional[str] = None
    status: str = "confirmed"
    created_at: str


class AvailabilityCheck(BaseModel):
    food_item: str
    date: str
    meal_type: str
    available: bool
    quantity_available: int
    message: str
    success: bool


@function_tool
def get_meal_of_the_day(date: str, meal_type: str = None) -> DayMealProgram:
    """
    Get the meal of the day for a specific date and meal type.
    
    Args:
        date: Date in YYYY-MM-DD format
        meal_type: Optional specific meal type (breakfast, lunch, dinner)
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        day_name = target_date.strftime("%A").lower()
        
        if day_name not in WEEKLY_MEAL_PROGRAM:
            return DayMealProgram(
                day=day_name,
                date=date,
                breakfast=MealOfTheDay(meal_type="breakfast", name="", description="", available=False, price=0),
                lunch=MealOfTheDay(meal_type="lunch", name="", description="", available=False, price=0),
                dinner=MealOfTheDay(meal_type="dinner", name="", description="", available=False, price=0),
                message=f"No meal program available for {day_name}",
                success=False
            )
        
        daily_program = WEEKLY_MEAL_PROGRAM[day_name]
        
        # Create meal objects with prices from menu
        meals = {}
        for meal_time in ["breakfast", "lunch", "dinner"]:
            meal_info = daily_program[meal_time]
            menu_item = next((item for item in RESTAURANT_MENU if item['name'] == meal_info['name']), None)
            
            meals[meal_time] = MealOfTheDay(
                meal_type=meal_time,
                name=meal_info['name'],
                description=meal_info['description'],
                available=menu_item['available'] if menu_item else False,
                price=menu_item['price'] if menu_item else 0
            )
        
        return DayMealProgram(
            day=day_name,
            date=date,
            breakfast=meals["breakfast"],
            lunch=meals["lunch"],
            dinner=meals["dinner"],
            message=f"Meal program for {day_name}, {date}",
            success=True
        )
        
    except ValueError:
        return DayMealProgram(
            day="",
            date=date,
            breakfast=MealOfTheDay(meal_type="breakfast", name="", description="", available=False, price=0),
            lunch=MealOfTheDay(meal_type="lunch", name="", description="", available=False, price=0),
            dinner=MealOfTheDay(meal_type="dinner", name="", description="", available=False, price=0),
            message="Invalid date format. Use YYYY-MM-DD",
            success=False
        )


@function_tool
def get_weekly_meal_schedule(start_date: str = None) -> WeeklySchedule:
    """
    Get the weekly meal schedule starting from a specific date.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to current week)
    """
    if start_date:
        try:
            base_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            base_date = datetime.now()
    else:
        base_date = datetime.now()
    
    # Find the start of the week (Monday)
    days_since_monday = base_date.weekday()
    week_start = base_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    daily_programs = []
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        daily_program = get_meal_of_the_day(date_str)
        daily_programs.append(daily_program)
    
    return WeeklySchedule(
        week_start=week_start.strftime("%Y-%m-%d"),
        week_end=week_end.strftime("%Y-%m-%d"),
        daily_programs=daily_programs,
        message=f"Weekly schedule from {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}",
        success=True
    )


@function_tool
def check_food_availability_by_date(food_item: str, date: str, meal_type: str) -> AvailabilityCheck:
    """
    Check if a specific food item is available on a given date and meal type.
    
    Args:
        food_item: Name of the food item
        date: Date in YYYY-MM-DD format
        meal_type: Meal type (breakfast, lunch, dinner)
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        day_name = target_date.strftime("%A").lower()
        
        # Find the menu item
        menu_item = next((item for item in RESTAURANT_MENU if item['name'].lower() == food_item.lower()), None)
        
        if not menu_item:
            return AvailabilityCheck(
                food_item=food_item,
                date=date,
                meal_type=meal_type,
                available=False,
                quantity_available=0,
                message=f"Food item '{food_item}' not found in menu",
                success=False
            )
        
        # Check if available on this day
        if day_name not in menu_item['available_days']:
            return AvailabilityCheck(
                food_item=food_item,
                date=date,
                meal_type=meal_type,
                available=False,
                quantity_available=0,
                message=f"{food_item} is not available on {day_name}",
                success=True
            )
        
        # Check if available for this meal type
        if meal_type not in menu_item['meal_types']:
            return AvailabilityCheck(
                food_item=food_item,
                date=date,
                meal_type=meal_type,
                available=False,
                quantity_available=0,
                message=f"{food_item} is not available for {meal_type}",
                success=True
            )
        
        # Check current stock
        available = menu_item['available'] and menu_item['quantity'] > 0
        
        return AvailabilityCheck(
            food_item=food_item,
            date=date,
            meal_type=meal_type,
            available=available,
            quantity_available=menu_item['quantity'],
            message=f"{food_item} is {'available' if available else 'not available'} for {meal_type} on {date}",
            success=True
        )
        
    except ValueError:
        return AvailabilityCheck(
            food_item=food_item,
            date=date,
            meal_type=meal_type,
            available=False,
            quantity_available=0,
            message="Invalid date format. Use YYYY-MM-DD",
            success=False
        )


@function_tool
def make_food_reservation(food_item: str, date: str, meal_type: str, quantity: int = 1,
                         customer_name: str = None, room_number: int = None,
                         customizations: List[str] = None, special_instructions: str = None) -> FoodReservation:
    """
    Make a food reservation for a future date.
    
    Args:
        food_item: Name of the food item to reserve
        date: Date for the reservation (YYYY-MM-DD)
        meal_type: Meal type (breakfast, lunch, dinner)
        quantity: Quantity to reserve
        customer_name: Name of the customer
        room_number: Room number if applicable
        customizations: List of customizations
        special_instructions: Special instructions
    """
    # Check availability first
    availability = check_food_availability_by_date(food_item, date, meal_type)
    
    if not availability.success or not availability.available:
        return FoodReservation(
            reservation_id="",
            food_item=food_item,
            meal_type=meal_type,
            scheduled_date=date,
            scheduled_time="",
            quantity=quantity,
            total_price=0.0,
            message=availability.message,
            status="failed",
            created_at=datetime.now().isoformat()
        )
    
    if quantity > availability.quantity_available:
        return FoodReservation(
            reservation_id="",
            food_item=food_item,
            meal_type=meal_type,
            scheduled_date=date,
            scheduled_time="",
            quantity=quantity,
            total_price=0.0,
            message=f"Only {availability.quantity_available} available, requested {quantity}",
            status="failed",
            created_at=datetime.now().isoformat()
        )
    
    # Find the menu item for pricing
    menu_item = next((item for item in RESTAURANT_MENU if item['name'].lower() == food_item.lower()), None)
    unit_price = menu_item['price']
    total_price = unit_price * quantity
    
    # Generate reservation ID
    reservation_id = f"RES-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(food_item + date) % 1000:03d}"
    
    # Set meal times
    meal_times = {
        "breakfast": "08:00",
        "lunch": "12:00", 
        "dinner": "19:00"
    }
    
    # Create reservation
    reservation = FoodReservation(
        reservation_id=reservation_id,
        customer_name=customer_name,
        room_number=room_number,
        food_item=food_item,
        meal_type=meal_type,
        scheduled_date=date,
        scheduled_time=meal_times.get(meal_type, "12:00"),
        quantity=quantity,
        total_price=total_price,
        customizations=customizations,
        special_instructions=special_instructions,
        status="confirmed",
        created_at=datetime.now().isoformat()
    )
    
    # Add to reservations list
    FOOD_RESERVATIONS.append(reservation.dict())
    
    # Reserve the quantity (decrease available stock for that date)
    menu_item['quantity'] -= quantity
    if menu_item['quantity'] <= 0:
        menu_item['available'] = False
    
    return reservation


@function_tool
def get_food_reservations(customer_name: str = None, room_number: int = None, date: str = None) -> Dict[str, Any]:
    """
    Get food reservations based on filters.
    
    Args:
        customer_name: Filter by customer name
        room_number: Filter by room number
        date: Filter by date (YYYY-MM-DD)
    """
    filtered_reservations = []
    
    for reservation in FOOD_RESERVATIONS:
        include = True
        
        if customer_name and reservation.get('customer_name') != customer_name:
            include = False
        if room_number and reservation.get('room_number') != room_number:
            include = False
        if date and reservation.get('scheduled_date') != date:
            include = False
            
        if include:
            filtered_reservations.append(reservation)
    
    return {
        "reservations": filtered_reservations,
        "count": len(filtered_reservations),
        "message": f"Found {len(filtered_reservations)} reservations",
        "success": True
    }


@function_tool
def cancel_food_reservation(reservation_id: str) -> Dict[str, Any]:
    """
    Cancel a food reservation and restore stock.
    
    Args:
        reservation_id: The reservation ID to cancel
    """
    reservation_index = None
    reservation_data = None
    
    for i, reservation in enumerate(FOOD_RESERVATIONS):
        if reservation['reservation_id'] == reservation_id:
            reservation_index = i
            reservation_data = reservation
            break
    
    if reservation_index is None:
        return {
            "message": f"Reservation {reservation_id} not found",
            "success": False
        }
    
    # Restore stock
    menu_item = next((item for item in RESTAURANT_MENU 
                     if item['name'].lower() == reservation_data['food_item'].lower()), None)
    
    if menu_item:
        menu_item['quantity'] += reservation_data['quantity']
        menu_item['available'] = True
    
    # Remove reservation
    FOOD_RESERVATIONS.pop(reservation_index)
    
    return {
        "reservation_id": reservation_id,
        "message": f"Reservation {reservation_id} cancelled successfully",
        "success": True
    }
