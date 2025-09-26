import random
from datetime import datetime, timedelta

def initialize_rooms():
    """Initializes a simulated database of hotel rooms with proper room numbers and random availability."""
    room_configs = [
        # Single rooms (100-104)
        {"number": 101, "type": "single", "price": 100, "floor": 1},
        {"number": 102, "type": "single", "price": 100, "floor": 1},
        {"number": 103, "type": "single", "price": 100, "floor": 1},
        {"number": 201, "type": "single", "price": 100, "floor": 2},
        {"number": 202, "type": "single", "price": 100, "floor": 2},
        
        # Double rooms (200-300 series)
        {"number": 203, "type": "double", "price": 150, "floor": 2},
        {"number": 204, "type": "double", "price": 150, "floor": 2},
        {"number": 205, "type": "double", "price": 150, "floor": 2},
        {"number": 301, "type": "double", "price": 150, "floor": 3},
        {"number": 302, "type": "double", "price": 150, "floor": 3},
        
        # Triple rooms (300+ series)
        {"number": 303, "type": "triple", "price": 200, "floor": 3},
        {"number": 304, "type": "triple", "price": 200, "floor": 3},
        {"number": 305, "type": "triple", "price": 200, "floor": 3},
        {"number": 401, "type": "triple", "price": 200, "floor": 4},
        {"number": 402, "type": "triple", "price": 200, "floor": 4},
    ]
    
    rooms = []
    for config in room_configs:
        rooms.append({
            "number": config["number"],
            "type": config["type"],
            "floor": config["floor"],
            "price_per_night": config["price"],
            "available": random.choice([True, False])
        })
    return rooms

def initialize_menu():
    """Initializes a simulated restaurant menu with quantity tracking and customization options."""
    menu_items = [
        {
            "name": "Pepperoni Pizza", 
            "price": 15, 
            "base_quantity": 20,
            "category": "pizza",
            "meal_types": ["lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "sizes": "medium",
                "half_toppings": "pepperoni",
                "crust": "regular"
            },
            "customization_options": {
                "sizes": {
                    "small": {"price_modifier": -2, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},  # base price
                    "large": {"price_modifier": 3, "name": "Large"}
                },
                "half_toppings": {
                    "pepperoni": {"price_modifier": 0, "name": "Pepperoni"},
                    "vegetable": {"price_modifier": -1, "name": "Vegetables"},
                    "cheese": {"price_modifier": -2, "name": "Extra Cheese"},
                    "mushroom": {"price_modifier": 1, "name": "Mushroom"},
                    "sausage": {"price_modifier": 2, "name": "Italian Sausage"}
                },
                "extras": {
                    "extra_cheese": {"price_modifier": 2, "name": "Extra Cheese"},
                    "gluten_free": {"price_modifier": 3, "name": "Gluten Free Base"},
                    "thin_crust": {"price_modifier": 1, "name": "Thin Crust"}
                }
            }
        },
        {
            "name": "Vegetable Pizza", 
            "price": 12, 
            "base_quantity": 15,
            "category": "pizza",
            "meal_types": ["lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "sizes": "medium",
                "half_toppings": "vegetable",
                "crust": "regular"
            },
            "customization_options": {
                "sizes": {
                    "small": {"price_modifier": -2, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 3, "name": "Large"}
                },
                "half_toppings": {
                    "vegetable": {"price_modifier": 0, "name": "Mixed Vegetables"},
                    "pepperoni": {"price_modifier": 2, "name": "Pepperoni"},
                    "cheese": {"price_modifier": -1, "name": "Extra Cheese"},
                    "mushroom": {"price_modifier": 0, "name": "Mushroom"},
                    "olives": {"price_modifier": 1, "name": "Olives"}
                },
                "extras": {
                    "extra_cheese": {"price_modifier": 2, "name": "Extra Cheese"},
                    "gluten_free": {"price_modifier": 3, "name": "Gluten Free Base"},
                    "vegan_cheese": {"price_modifier": 4, "name": "Vegan Cheese"}
                }
            }
        },
        {
            "name": "Cheeseburger", 
            "price": 10, 
            "base_quantity": 25,
            "category": "burger",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "patty_cook": "medium",
                "sides": "no_side"
            },
            "customization_options": {
                "patty_cook": {
                    "rare": {"price_modifier": 0, "name": "Rare"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "well_done": {"price_modifier": 0, "name": "Well Done"}
                },
                "extras": {
                    "bacon": {"price_modifier": 3, "name": "Bacon"},
                    "extra_cheese": {"price_modifier": 2, "name": "Extra Cheese"},
                    "avocado": {"price_modifier": 2, "name": "Avocado"},
                    "mushrooms": {"price_modifier": 1, "name": "Grilled Mushrooms"}
                },
                "sides": {
                    "no_side": {"price_modifier": 0, "name": "No Side"},
                    "fries": {"price_modifier": 3, "name": "French Fries"},
                    "onion_rings": {"price_modifier": 4, "name": "Onion Rings"},
                    "salad": {"price_modifier": 5, "name": "Side Salad"}
                }
            }
        },
        {
            "name": "Caesar Salad", 
            "price": 8, 
            "base_quantity": 30,
            "category": "salad",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "protein": "no_protein",
                "dressing": "caesar"
            },
            "customization_options": {
                "protein": {
                    "no_protein": {"price_modifier": 0, "name": "No Protein"},
                    "chicken": {"price_modifier": 4, "name": "Grilled Chicken"},
                    "shrimp": {"price_modifier": 6, "name": "Grilled Shrimp"},
                    "salmon": {"price_modifier": 8, "name": "Grilled Salmon"}
                },
                "dressing": {
                    "caesar": {"price_modifier": 0, "name": "Caesar Dressing"},
                    "ranch": {"price_modifier": 0, "name": "Ranch Dressing"},
                    "vinaigrette": {"price_modifier": 0, "name": "Balsamic Vinaigrette"}
                }
            }
        },
        {
            "name": "Soft Drink", 
            "price": 2, 
            "base_quantity": 50,
            "category": "beverage",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "type": "cola",
                "size": "medium",
                "sugar": "normal"
            },
            "customization_options": {
                "type": {
                    "cola": {"price_modifier": 0, "name": "Cola"},
                    "sprite": {"price_modifier": 0, "name": "Sprite"},
                    "orange": {"price_modifier": 0, "name": "Orange Soda"},
                    "water": {"price_modifier": -0.5, "name": "Sparkling Water"}
                },
                "size": {
                    "small": {"price_modifier": -0.5, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 1, "name": "Large"}
                },
                "sugar": {
                    "no_sugar": {"price_modifier": 0, "name": "No Sugar"},
                    "low_sugar": {"price_modifier": 0, "name": "Low Sugar"},
                    "normal": {"price_modifier": 0, "name": "Normal Sugar"},
                    "extra_sweet": {"price_modifier": 0.5, "name": "Extra Sweet"}
                },
                "extras": {
                    "ice": {"price_modifier": 0, "name": "With Ice"},
                    "no_ice": {"price_modifier": 0, "name": "No Ice"},
                    "lemon": {"price_modifier": 0.5, "name": "Fresh Lemon"},
                    "lime": {"price_modifier": 0.5, "name": "Fresh Lime"}
                }
            }
        },
        {
            "name": "Fresh Juice",
            "price": 4,
            "base_quantity": 25,
            "category": "beverage",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "type": "orange",
                "size": "medium",
                "sugar": "no_sugar"
            },
            "customization_options": {
                "type": {
                    "orange": {"price_modifier": 0, "name": "Fresh Orange"},
                    "apple": {"price_modifier": 0, "name": "Fresh Apple"},
                    "carrot": {"price_modifier": 0.5, "name": "Fresh Carrot"},
                    "mixed_fruit": {"price_modifier": 1, "name": "Mixed Fruit"},
                    "pomegranate": {"price_modifier": 1.5, "name": "Pomegranate"}
                },
                "size": {
                    "small": {"price_modifier": -1, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 1.5, "name": "Large"}
                },
                "sugar": {
                    "no_sugar": {"price_modifier": 0, "name": "No Added Sugar"},
                    "honey": {"price_modifier": 0.5, "name": "Natural Honey"},
                    "sugar": {"price_modifier": 0, "name": "Regular Sugar"}
                },
                "extras": {
                    "ice": {"price_modifier": 0, "name": "With Ice"},
                    "mint": {"price_modifier": 0.5, "name": "Fresh Mint"},
                    "ginger": {"price_modifier": 0.5, "name": "Fresh Ginger"}
                }
            }
        },
        {
            "name": "Coffee",
            "price": 3,
            "base_quantity": 40,
            "category": "hot_beverage",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "type": "espresso",
                "size": "medium",
                "sugar": "normal",
                "milk": "regular"
            },
            "customization_options": {
                "type": {
                    "espresso": {"price_modifier": 0, "name": "Espresso"},
                    "americano": {"price_modifier": 0, "name": "Americano"},
                    "cappuccino": {"price_modifier": 1, "name": "Cappuccino"},
                    "latte": {"price_modifier": 1.5, "name": "Latte"},
                    "mocha": {"price_modifier": 2, "name": "Mocha"}
                },
                "size": {
                    "small": {"price_modifier": -0.5, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 1, "name": "Large"}
                },
                "sugar": {
                    "no_sugar": {"price_modifier": 0, "name": "No Sugar"},
                    "low_sugar": {"price_modifier": 0, "name": "1 Sugar"},
                    "normal": {"price_modifier": 0, "name": "2 Sugars"},
                    "extra_sweet": {"price_modifier": 0, "name": "3+ Sugars"}
                },
                "milk": {
                    "no_milk": {"price_modifier": 0, "name": "Black"},
                    "regular": {"price_modifier": 0, "name": "Regular Milk"},
                    "almond": {"price_modifier": 0.5, "name": "Almond Milk"},
                    "soy": {"price_modifier": 0.5, "name": "Soy Milk"},
                    "oat": {"price_modifier": 0.75, "name": "Oat Milk"}
                },
                "extras": {
                    "decaf": {"price_modifier": 0, "name": "Decaffeinated"},
                    "extra_shot": {"price_modifier": 1, "name": "Extra Shot"},
                    "vanilla": {"price_modifier": 0.5, "name": "Vanilla Syrup"},
                    "caramel": {"price_modifier": 0.5, "name": "Caramel Syrup"}
                }
            }
        },
        {
            "name": "Tea",
            "price": 2.5,
            "base_quantity": 35,
            "category": "hot_beverage",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "type": "black_tea",
                "size": "medium",
                "sugar": "normal"
            },
            "customization_options": {
                "type": {
                    "black_tea": {"price_modifier": 0, "name": "Black Tea"},
                    "green_tea": {"price_modifier": 0, "name": "Green Tea"},
                    "chamomile": {"price_modifier": 0.5, "name": "Chamomile"},
                    "earl_grey": {"price_modifier": 0.5, "name": "Earl Grey"},
                    "persian_tea": {"price_modifier": 0.5, "name": "Persian Tea"}
                },
                "size": {
                    "small": {"price_modifier": -0.5, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 0.5, "name": "Large"}
                },
                "sugar": {
                    "no_sugar": {"price_modifier": 0, "name": "No Sugar"},
                    "honey": {"price_modifier": 0.5, "name": "Natural Honey"},
                    "normal": {"price_modifier": 0, "name": "Regular Sugar"},
                    "extra_sweet": {"price_modifier": 0, "name": "Extra Sweet"}
                },
                "extras": {
                    "lemon": {"price_modifier": 0.5, "name": "Fresh Lemon"},
                    "milk": {"price_modifier": 0.5, "name": "Add Milk"},
                    "mint": {"price_modifier": 0.5, "name": "Fresh Mint"},
                    "cardamom": {"price_modifier": 0.5, "name": "Cardamom"}
                }
            }
        },
        {
            "name": "Smoothie",
            "price": 6,
            "base_quantity": 20,
            "category": "beverage",
            "meal_types": ["breakfast", "lunch"],
            "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "base": "banana_strawberry",
                "size": "medium",
                "sweetener": "natural"
            },
            "customization_options": {
                "base": {
                    "banana_strawberry": {"price_modifier": 0, "name": "Banana Strawberry"},
                    "mango_pineapple": {"price_modifier": 0.5, "name": "Mango Pineapple"},
                    "berry_mix": {"price_modifier": 1, "name": "Mixed Berry"},
                    "green_detox": {"price_modifier": 1.5, "name": "Green Detox"},
                    "protein_power": {"price_modifier": 2, "name": "Protein Power"}
                },
                "size": {
                    "small": {"price_modifier": -1.5, "name": "Small"},
                    "medium": {"price_modifier": 0, "name": "Medium"},
                    "large": {"price_modifier": 2, "name": "Large"}
                },
                "sweetener": {
                    "no_sweetener": {"price_modifier": 0, "name": "No Sweetener"},
                    "natural": {"price_modifier": 0, "name": "Natural Fruit"},
                    "honey": {"price_modifier": 0.5, "name": "Honey"},
                    "agave": {"price_modifier": 0.75, "name": "Agave Syrup"}
                },
                "extras": {
                    "protein_powder": {"price_modifier": 2, "name": "Protein Powder"},
                    "chia_seeds": {"price_modifier": 1, "name": "Chia Seeds"},
                    "coconut": {"price_modifier": 0.5, "name": "Coconut Flakes"},
                    "extra_fruit": {"price_modifier": 1, "name": "Extra Fruit"}
                }
            }
        },
        {
            "name": "Persian Kabob Koobideh", 
            "price": 25, 
            "base_quantity": 12,
            "category": "persian",
            "meal_types": ["lunch", "dinner"],
            "available_days": ["tuesday", "thursday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "spice_level": "medium",
                "sides": "rice"
            },
            "customization_options": {
                "spice_level": {
                    "mild": {"price_modifier": 0, "name": "Mild"},
                    "medium": {"price_modifier": 0, "name": "Medium Spicy"},
                    "hot": {"price_modifier": 1, "name": "Hot"},
                    "extra_hot": {"price_modifier": 2, "name": "Extra Hot"}
                },
                "sides": {
                    "rice": {"price_modifier": 3, "name": "Saffron Rice"},
                    "bread": {"price_modifier": 2, "name": "Persian Bread"},
                    "salad": {"price_modifier": 4, "name": "Shirazi Salad"},
                    "yogurt": {"price_modifier": 3, "name": "Persian Yogurt"}
                }
            }
        },
        {
            "name": "Saffron Joojeh Kabab", 
            "price": 22, 
            "base_quantity": 18,
            "category": "persian",
            "meal_types": ["lunch", "dinner"],
            "available_days": ["monday", "wednesday", "friday", "saturday", "sunday"],
            "customizable": True,
            "defaults": {
                "marinade": "saffron",
                "sides": "rice"
            },
            "customization_options": {
                "marinade": {
                    "saffron": {"price_modifier": 0, "name": "Traditional Saffron"},
                    "herb": {"price_modifier": 1, "name": "Herb Marinade"},
                    "spicy": {"price_modifier": 1, "name": "Spicy Marinade"}
                },
                "sides": {
                    "rice": {"price_modifier": 3, "name": "Saffron Rice"},
                    "grilled_tomato": {"price_modifier": 2, "name": "Grilled Tomato"},
                    "salad": {"price_modifier": 4, "name": "Shirazi Salad"}
                }
            }
        }
    ]
    
    menu = []
    for item in menu_items:
        # Random quantity between 0 and base_quantity
        current_quantity = random.randint(0, item["base_quantity"])
        menu.append({
            "name": item["name"],
            "price": item["price"],
            "quantity": current_quantity,
            "available": current_quantity > 0,
            "category": item["category"],
            "meal_types": item["meal_types"],
            "available_days": item["available_days"],
            "customizable": item["customizable"],
            "customization_options": item["customization_options"],
            "defaults": item.get("defaults", {})
        })
    return menu

def initialize_weekly_meal_program():
    """Initialize the meal of the day program for each day of the week."""
    weekly_meals = {
        "monday": {
            "breakfast": {"name": "Fresh Juice", "description": "Energizing Orange Juice to start your week"},
            "lunch": {"name": "Caesar Salad", "description": "Healthy start with grilled chicken"},
            "dinner": {"name": "Saffron Joojeh Kabab", "description": "Traditional Persian flavors"}
        },
        "tuesday": {
            "breakfast": {"name": "Coffee", "description": "Premium espresso blend"},
            "lunch": {"name": "Cheeseburger", "description": "Classic American favorite"},
            "dinner": {"name": "Persian Kabob Koobideh", "description": "Authentic Persian ground meat kabab"}
        },
        "wednesday": {
            "breakfast": {"name": "Smoothie", "description": "Mixed berry protein smoothie"},
            "lunch": {"name": "Vegetable Pizza", "description": "Fresh garden vegetables on thin crust"},
            "dinner": {"name": "Saffron Joojeh Kabab", "description": "Tender chicken with saffron marinade"}
        },
        "thursday": {
            "breakfast": {"name": "Tea", "description": "Traditional Persian tea with cardamom"},
            "lunch": {"name": "Pepperoni Pizza", "description": "Classic pepperoni on medium crust"},
            "dinner": {"name": "Persian Kabob Koobideh", "description": "Spicy ground beef kabab"}
        },
        "friday": {
            "breakfast": {"name": "Coffee", "description": "Cappuccino with extra foam"},
            "lunch": {"name": "Caesar Salad", "description": "With grilled salmon upgrade"},
            "dinner": {"name": "Persian Kabob Koobideh", "description": "Friday special with extra rice"}
        },
        "saturday": {
            "breakfast": {"name": "Fresh Juice", "description": "Mixed fruit juice blend"},
            "lunch": {"name": "Cheeseburger", "description": "Weekend special with bacon"},
            "dinner": {"name": "Saffron Joojeh Kabab", "description": "Weekend family special"}
        },
        "sunday": {
            "breakfast": {"name": "Smoothie", "description": "Green detox smoothie"},
            "lunch": {"name": "Pepperoni Pizza", "description": "Sunday family pizza"},
            "dinner": {"name": "Persian Kabob Koobideh", "description": "Sunday dinner with yogurt"}
        }
    }
    return weekly_meals


def initialize_restaurant_tables():
    """Initialize restaurant tables with different capacities."""
    table_configs = [
        # 4-person tables
        {"table_number": 1, "capacity": 4, "location": "window"},
        {"table_number": 2, "capacity": 4, "location": "center"},
        {"table_number": 3, "capacity": 4, "location": "corner"},
        {"table_number": 4, "capacity": 4, "location": "window"},
        
        # 5-person tables
        {"table_number": 5, "capacity": 5, "location": "center"},
        {"table_number": 6, "capacity": 5, "location": "private"},
        {"table_number": 7, "capacity": 5, "location": "window"},
        
        # 6-person tables
        {"table_number": 8, "capacity": 6, "location": "family_area"},
        {"table_number": 9, "capacity": 6, "location": "center"},
        {"table_number": 10, "capacity": 6, "location": "private"},
        
        # 10-person tables (large groups)
        {"table_number": 11, "capacity": 10, "location": "private_room"},
        {"table_number": 12, "capacity": 10, "location": "banquet_area"},
    ]
    
    tables = []
    for config in table_configs:
        tables.append({
            "table_number": config["table_number"],
            "capacity": config["capacity"],
            "location": config["location"],
            "available": random.choice([True, False]),  # Random availability
            "reserved_by": None,
            "reserved_date": None,
            "reserved_time": None,
            "reservation_duration": None
        })
    return tables


def initialize_food_reservations():
    """Initialize the food reservation system."""
    return []  # Will store reservation records


def initialize_table_reservations():
    """Initialize the table reservation system."""
    return []  # Will store table reservation records


# Initialize the databases
HOTEL_ROOMS = initialize_rooms()
RESTAURANT_MENU = initialize_menu()
WEEKLY_MEAL_PROGRAM = initialize_weekly_meal_program()
FOOD_RESERVATIONS = initialize_food_reservations()
RESTAURANT_TABLES = initialize_restaurant_tables()
TABLE_RESERVATIONS = initialize_table_reservations()
