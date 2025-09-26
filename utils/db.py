import random

def initialize_rooms():
    """Initializes a simulated database of hotel rooms with random availability."""
    room_types = {
        "single": {"price": 100, "capacity": 1},
        "double": {"price": 150, "capacity": 2},
        "triple": {"price": 200, "capacity": 3},
    }
    rooms = []
    for room_type, details in room_types.items():
        for i in range(5):  # Create 5 rooms of each type
            rooms.append({
                "id": f"{room_type}_{i+1}",
                "type": room_type,
                "price_per_night": details["price"],
                "available": random.choice([True, False])
            })
    return rooms

def initialize_menu():
    """Initializes a simulated restaurant menu with random availability."""
    menu_items = [
        {"name": "Pepperoni Pizza", "price": 15},
        {"name": "Vegetable Pizza", "price": 12},
        {"name": "Cheeseburger", "price": 10},
        {"name": "Caesar Salad", "price": 8},
        {"name": "Soft Drink", "price": 2},
        {"name": "Persian Kabob Koobideh", "price": 25},
        {"name": "Saffron Joojeh Kabab", "price": 22},
    ]
    menu = []
    for item in menu_items:
        menu.append({
            "name": item["name"],
            "price": item["price"],
            "available": random.choice([True, False])
        })
    return menu

# Initialize the databases
HOTEL_ROOMS = initialize_rooms()
RESTAURANT_MENU = initialize_menu()
