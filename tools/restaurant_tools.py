from typing import List
from pydantic import BaseModel
from agents import function_tool
from utils.db import RESTAURANT_MENU


class MenuItem(BaseModel):
    name: str
    price: float
    available: bool


class MenuResponse(BaseModel):
    items: List[MenuItem]
    message: str
    success: bool


class OrderItem(BaseModel):
    name: str
    quantity: int


class OrderedItem(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total_price: float


class FoodOrder(BaseModel):
    ordered_items: List[OrderedItem]
    unavailable_items: List[str]
    total_cost: float
    message: str
    success: bool


@function_tool
def get_menu_items() -> MenuResponse:
    """
    Retrieves the list of available menu items with structured data.
    """
    available_items = [item for item in RESTAURANT_MENU if item['available']]
    
    if not available_items:
        return MenuResponse(
            items=[],
            message="Sorry, the menu is not available at the moment.",
            success=False
        )
    
    menu_items = [
        MenuItem(name=item['name'], price=item['price'], available=item['available'])
        for item in available_items
    ]
    
    menu_text = "Available Menu Items:\n" + "\n".join(
        f"- {item.name}: ${item.price}" for item in menu_items
    )
    
    return MenuResponse(
        items=menu_items,
        message=menu_text,
        success=True
    )


@function_tool
def order_food(items: List[OrderItem]) -> FoodOrder:
    """
    Places a food order for a list of items with structured response.

    Args:
        items: A list of items to order, each with name and quantity.
    """
    total_cost = 0.0
    ordered_items = []
    unavailable_items = []

    for order_item in items:
        item_name = order_item.name
        quantity = order_item.quantity
        
        menu_item = next(
            (item for item in RESTAURANT_MENU 
             if item['name'].lower() == item_name.lower() and item['available']), 
            None
        )
        
        if menu_item:
            unit_price = menu_item['price']
            item_total = unit_price * quantity
            total_cost += item_total
            
            ordered_items.append(OrderedItem(
                name=menu_item['name'],
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total
            ))
        else:
            unavailable_items.append(item_name)
    
    if unavailable_items and not ordered_items:
        return FoodOrder(
            ordered_items=[],
            unavailable_items=unavailable_items,
            total_cost=0.0,
            message=f"Sorry, the following items are not available: {', '.join(unavailable_items)}.",
            success=False
        )
    
    if not ordered_items:
        return FoodOrder(
            ordered_items=[],
            unavailable_items=[],
            total_cost=0.0,
            message="You did not order any available items.",
            success=False
        )
    
    order_summary = [f"{item.quantity}x {item.name}" for item in ordered_items]
    message = f"Successfully placed order for: {', '.join(order_summary)}. Total cost: ${total_cost}."
    
    if unavailable_items:
        message += f" Note: These items were not available: {', '.join(unavailable_items)}."
    
    return FoodOrder(
        ordered_items=ordered_items,
        unavailable_items=unavailable_items,
        total_cost=total_cost,
        message=message,
        success=True
    )