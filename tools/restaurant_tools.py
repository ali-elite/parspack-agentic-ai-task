from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from agents import function_tool
from utils.db import RESTAURANT_MENU


class CustomizationOption(BaseModel):
    key: str
    name: str
    price_modifier: float


class CustomizationCategory(BaseModel):
    category: str
    options: List[CustomizationOption]


class MenuItem(BaseModel):
    name: str
    price: float
    quantity: int
    available: bool
    category: str
    customizable: bool
    customization_options: Optional[Dict[str, Any]] = None


class MenuResponse(BaseModel):
    items: List[MenuItem]
    message: str
    success: bool


class CustomizationRequest(BaseModel):
    category: str
    selected_options: List[str]


class OrderItem(BaseModel):
    name: str
    quantity: int
    customizations: Optional[List[CustomizationRequest]] = None
    special_instructions: Optional[str] = None
    service_type: str = "takeaway"  # "takeaway" or "dine_in"


class OrderedItem(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total_price: float
    customizations_applied: Optional[List[str]] = None
    special_instructions: Optional[str] = None
    service_type: str = "takeaway"


class FoodOrder(BaseModel):
    ordered_items: List[OrderedItem]
    unavailable_items: List[str]
    total_cost: float
    service_type: str = "takeaway"  # "takeaway" or "dine_in"
    table_number: Optional[int] = None  # Only for dine_in orders
    table_reservation_id: Optional[str] = None  # Only for dine_in orders
    message: str
    success: bool


class CustomizationDetails(BaseModel):
    item_name: str
    customization_categories: List[CustomizationCategory]
    base_price: float
    message: str
    success: bool


@function_tool
def get_menu_items() -> MenuResponse:
    """
    Retrieves the list of available menu items with structured data including quantities and customization info.
    """
    available_items = [item for item in RESTAURANT_MENU if item['available']]
    
    if not available_items:
        return MenuResponse(
            items=[],
            message="Sorry, the menu is not available at the moment.",
            success=False
        )
    
    menu_items = [
        MenuItem(
            name=item['name'], 
            price=item['price'], 
            quantity=item['quantity'], 
            available=item['available'],
            category=item['category'],
            customizable=item['customizable'],
            customization_options=item.get('customization_options')
        )
        for item in available_items
    ]
    
    menu_text = "Available Menu Items:\n" + "\n".join(
        f"- {item.name}: ${item.price} ({item.quantity} available)" + 
        (" - Customizable" if item.customizable else "")
        for item in menu_items
    )
    
    return MenuResponse(
        items=menu_items,
        message=menu_text,
        success=True
    )


@function_tool
def get_customization_options(item_name: str) -> CustomizationDetails:
    """
    Retrieves customization options for a specific menu item.
    
    Args:
        item_name: The name of the menu item to get customization options for.
    """
    menu_item = next(
        (item for item in RESTAURANT_MENU if item['name'].lower() == item_name.lower()),
        None
    )
    
    if not menu_item:
        return CustomizationDetails(
            item_name=item_name,
            customization_categories=[],
            base_price=0.0,
            message=f"Menu item '{item_name}' not found.",
            success=False
        )
    
    if not menu_item.get('customizable', False):
        return CustomizationDetails(
            item_name=item_name,
            customization_categories=[],
            base_price=menu_item['price'],
            message=f"{item_name} is not customizable.",
            success=False
        )
    
    customization_categories = []
    customization_options = menu_item.get('customization_options', {})
    
    for category, options in customization_options.items():
        category_options = [
            CustomizationOption(
                key=key,
                name=option['name'],
                price_modifier=option['price_modifier']
            )
            for key, option in options.items()
        ]
        customization_categories.append(
            CustomizationCategory(category=category, options=category_options)
        )
    
    # Create detailed message about customization options
    details_lines = [f"Customization options for {item_name} (Base price: ${menu_item['price']}):"]
    for category in customization_categories:
        details_lines.append(f"\n{category.category.replace('_', ' ').title()}:")
        for option in category.options:
            price_info = f" (+${option.price_modifier})" if option.price_modifier > 0 else f" (-${abs(option.price_modifier)})" if option.price_modifier < 0 else ""
            details_lines.append(f"  - {option.name}{price_info}")
    
    return CustomizationDetails(
        item_name=item_name,
        customization_categories=customization_categories,
        base_price=menu_item['price'],
        message="\n".join(details_lines),
        success=True
    )


def calculate_customized_price(base_price: float, customizations: List[CustomizationRequest], customization_options: Dict[str, Any], defaults: Dict[str, Any] = None) -> tuple[float, List[str]]:
    """
    Calculates the final price for a customized item and returns applied customizations.
    
    Args:
        base_price: The base price of the menu item
        customizations: List of customization requests
        customization_options: Available customization options for the item
        defaults: Default options for the item
        
    Returns:
        Tuple of (final_price, list of applied customization descriptions)
    """
    final_price = base_price
    applied_customizations = []
    defaults = defaults or {}
    
    # Start with defaults - apply default price modifiers
    for category, default_option in defaults.items():
        if category in customization_options:
            category_options = customization_options[category]
            if default_option in category_options:
                modifier = category_options[default_option]['price_modifier']
                final_price += modifier
                applied_customizations.append(f"{category_options[default_option]['name']} (default)")
    
    # Process custom requests (override defaults)
    requested_categories = set()
    for customization in customizations:
        category = customization.category
        selected_options = customization.selected_options
        requested_categories.add(category)
        
        # Remove default for this category since we're customizing it
        if category in defaults:
            default_option = defaults[category]
            if category in customization_options and default_option in customization_options[category]:
                default_modifier = customization_options[category][default_option]['price_modifier']
                final_price -= default_modifier
                # Remove default from applied customizations
                default_name = f"{customization_options[category][default_option]['name']} (default)"
                if default_name in applied_customizations:
                    applied_customizations.remove(default_name)
        
        if category in customization_options:
            category_options = customization_options[category]
            
            # Handle special case for half_toppings (pizza)
            if category == "half_toppings" and len(selected_options) == 2:
                # Half and half pizza
                half1, half2 = selected_options[0], selected_options[1]
                if half1 in category_options and half2 in category_options:
                    # Average the price modifiers for half-and-half
                    modifier1 = category_options[half1]['price_modifier']
                    modifier2 = category_options[half2]['price_modifier']
                    avg_modifier = (modifier1 + modifier2) / 2
                    final_price += avg_modifier
                    applied_customizations.append(f"Half {category_options[half1]['name']} / Half {category_options[half2]['name']}")
            else:
                # Regular customizations
                for option_key in selected_options:
                    if option_key in category_options:
                        modifier = category_options[option_key]['price_modifier']
                        final_price += modifier
                        applied_customizations.append(category_options[option_key]['name'])
    
    return final_price, applied_customizations


@function_tool
def order_food(items: List[OrderItem], table_reservation_id: str = None) -> FoodOrder:
    """
    Places a food order for a list of items with structured response, quantity tracking, and customization support.
    Supports both takeaway and dine-in service.

    Args:
        items: A list of items to order, each with name, quantity, and optional customizations.
        table_reservation_id: Optional table reservation ID for dine-in orders.
    """
    total_cost = 0.0
    ordered_items = []
    unavailable_items = []
    
    # Determine overall service type from items
    service_types = set()
    table_info = None
    
    # Import here to avoid circular imports
    from utils.db import TABLE_RESERVATIONS
    
    # Check if this is related to a table reservation
    if table_reservation_id:
        table_reservation = next(
            (res for res in TABLE_RESERVATIONS if res['reservation_id'] == table_reservation_id), 
            None
        )
        if table_reservation:
            table_info = {
                'table_number': table_reservation['table_number'],
                'reservation_id': table_reservation_id
            }

    for order_item in items:
        item_name = order_item.name
        requested_quantity = order_item.quantity
        customizations = order_item.customizations or []
        special_instructions = order_item.special_instructions
        item_service_type = order_item.service_type
        service_types.add(item_service_type)
        
        menu_item = next(
            (item for item in RESTAURANT_MENU 
             if item['name'].lower() == item_name.lower() and item['available']), 
            None
        )
        
        if menu_item:
            available_quantity = menu_item['quantity']
            
            # Check if we have enough quantity
            if requested_quantity <= available_quantity:
                # Calculate customized price
                base_price = menu_item['price']
                customization_options = menu_item.get('customization_options', {})
                defaults = menu_item.get('defaults', {})
                
                if customizations or defaults:
                    unit_price, applied_customizations = calculate_customized_price(
                        base_price, customizations or [], customization_options, defaults
                    )
                else:
                    unit_price = base_price
                    applied_customizations = []
                
                item_total = unit_price * requested_quantity
                total_cost += item_total
                
                # Decrease the stock
                menu_item['quantity'] -= requested_quantity
                
                # Update availability status
                if menu_item['quantity'] == 0:
                    menu_item['available'] = False
                
                ordered_items.append(OrderedItem(
                    name=menu_item['name'],
                    quantity=requested_quantity,
                    unit_price=unit_price,
                    total_price=item_total,
                    customizations_applied=applied_customizations if applied_customizations else None,
                    special_instructions=special_instructions,
                    service_type=item_service_type
                ))
            else:
                # Not enough stock
                if available_quantity > 0:
                    unavailable_items.append(f"{item_name} (requested {requested_quantity}, only {available_quantity} available)")
                else:
                    unavailable_items.append(f"{item_name} (out of stock)")
        else:
            unavailable_items.append(f"{item_name} (not on menu or out of stock)")
    
    # Determine the primary service type
    primary_service_type = "takeaway"  # Default
    if "dine_in" in service_types:
        primary_service_type = "dine_in"
    elif service_types:
        primary_service_type = list(service_types)[0]
    
    if unavailable_items and not ordered_items:
        return FoodOrder(
            ordered_items=[],
            unavailable_items=unavailable_items,
            total_cost=0.0,
            service_type=primary_service_type,
            table_number=table_info['table_number'] if table_info else None,
            table_reservation_id=table_info['reservation_id'] if table_info else None,
            message=f"Sorry, we couldn't fulfill your order. Issues: {', '.join(unavailable_items)}.",
            success=False
        )
    
    if not ordered_items:
        return FoodOrder(
            ordered_items=[],
            unavailable_items=[],
            total_cost=0.0,
            service_type=primary_service_type,
            table_number=table_info['table_number'] if table_info else None,
            table_reservation_id=table_info['reservation_id'] if table_info else None,
            message="You did not order any available items.",
            success=False
        )
    
    # Create detailed order summary
    order_details = []
    for item in ordered_items:
        item_detail = f"{item.quantity}x {item.name}"
        if item.customizations_applied:
            item_detail += f" (with {', '.join(item.customizations_applied)})"
        if item.special_instructions:
            item_detail += f" - Special: {item.special_instructions}"
        item_detail += f" - ${item.total_price:.2f} ({item.service_type})"
        order_details.append(item_detail)
    
    # Create service-specific message
    service_message = f"Successfully placed {primary_service_type} order"
    if table_info:
        service_message += f" for Table {table_info['table_number']}"
    
    message = f"{service_message}:\n" + "\n".join(order_details) + f"\n\nTotal cost: ${total_cost:.2f}"
    
    if unavailable_items:
        message += f"\n\nNote: These items had issues: {', '.join(unavailable_items)}."
    
    return FoodOrder(
        ordered_items=ordered_items,
        unavailable_items=unavailable_items,
        total_cost=total_cost,
        service_type=primary_service_type,
        table_number=table_info['table_number'] if table_info else None,
        table_reservation_id=table_info['reservation_id'] if table_info else None,
        message=message,
        success=True
    )


@function_tool
def create_half_taste_pizza_order(pizza_base: str, first_half: str, second_half: str, size: str = "medium", quantity: int = 1, extras: List[str] = None, service_type: str = "takeaway", table_reservation_id: str = None) -> FoodOrder:
    """
    Creates a customized half-taste pizza order easily.
    
    Args:
        pizza_base: Base pizza type (e.g., "Pepperoni Pizza", "Vegetable Pizza")
        first_half: Topping for first half (e.g., "pepperoni", "vegetable")
        second_half: Topping for second half (e.g., "mushroom", "sausage")
        size: Pizza size ("small", "medium", "large")
        quantity: Number of pizzas to order
        extras: Optional list of extra toppings (e.g., ["extra_cheese", "thin_crust"])
        service_type: Service type ("takeaway" or "dine_in")
        table_reservation_id: Optional table reservation ID for dine-in orders
    """
    customizations = [
        CustomizationRequest(category="sizes", selected_options=[size]),
        CustomizationRequest(category="half_toppings", selected_options=[first_half, second_half])
    ]
    
    if extras:
        customizations.append(CustomizationRequest(category="extras", selected_options=extras))
    
    order_item = OrderItem(
        name=pizza_base,
        quantity=quantity,
        customizations=customizations,
        special_instructions=f"Half {first_half}, half {second_half}",
        service_type=service_type
    )
    
    return order_food([order_item], table_reservation_id)