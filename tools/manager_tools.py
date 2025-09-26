from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from agents import function_tool


class ReceiptItem(BaseModel):
    item_name: str
    quantity: int
    unit_price: float
    total_price: float
    customizations: Optional[List[str]] = None
    special_instructions: Optional[str] = None
    category: str  # "room", "food", "service"


class DiscountConditions(BaseModel):
    category: Optional[str] = None
    min_items: Optional[int] = None
    free_items: Optional[int] = None
    nights: Optional[int] = None

class DiscountRule(BaseModel):
    rule_type: str  # "percentage", "fixed_amount", "buy_x_get_y"
    value: float
    description: str
    conditions: Optional[DiscountConditions] = None


class Invoice(BaseModel):
    invoice_id: str
    customer_name: Optional[str] = None
    room_number: Optional[int] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    items: List[ReceiptItem]
    subtotal: float
    discounts: List[str] = []
    tax_rate: float
    tax_amount: float
    service_charge: float
    total_amount: float
    payment_status: str = "pending"
    created_at: str


class PaymentSummary(BaseModel):
    total_rooms_revenue: float
    total_food_revenue: float
    total_service_revenue: float
    total_discounts: float
    total_taxes: float
    net_revenue: float
    items_count: int
    message: str
    success: bool


class OrderedFoodItem(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total_price: float
    customizations_applied: Optional[List[str]] = None
    special_instructions: Optional[str] = None


class RoomBookingInput(BaseModel):
    success: bool = True
    room_number: Optional[int] = None
    room_type: Optional[str] = None
    nights: Optional[int] = None
    total_cost: Optional[float] = None
    floor: Optional[int] = None


class FoodOrderInput(BaseModel):
    success: bool = True
    ordered_items: Optional[List[OrderedFoodItem]] = None


class ReceiptCalculation(BaseModel):
    subtotal: float
    discount_amount: float
    applied_discounts: List[str] = []
    service_charge: float
    tax_amount: float
    total_amount: float
    message: str
    success: bool


class DiscountResult(BaseModel):
    discount_amount: float
    message: str
    success: bool


class StayCostResult(BaseModel):
    room_number: Optional[int] = None
    nights: Optional[int] = None
    price_per_night: Optional[float] = None
    room_cost: Optional[float] = None
    service_cost: Optional[float] = None
    total_cost: Optional[float] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    message: str
    success: bool


@function_tool
def calculate_receipt_total(items: List[ReceiptItem], tax_rate: float = 0.08, service_charge_rate: float = 0.10, discounts: List[DiscountRule] = None) -> ReceiptCalculation:
    """
    Calculates the total amount for a receipt including taxes, service charges, and discounts.
    
    Args:
        items: List of receipt items with prices
        tax_rate: Tax rate (default 8%)
        service_charge_rate: Service charge rate (default 10%)
        discounts: Optional list of discount rules to apply
    """
    if not items:
        return ReceiptCalculation(
            subtotal=0.0,
            discount_amount=0.0,
            applied_discounts=[],
            service_charge=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            message="No items to calculate",
            success=False
        )
    
    # Calculate subtotal
    subtotal = sum(item.total_price for item in items)
    
    # Apply discounts
    discount_amount = 0.0
    applied_discounts = []
    
    if discounts:
        for discount in discounts:
            if discount.rule_type == "percentage":
                discount_value = subtotal * (discount.value / 100)
                discount_amount += discount_value
                applied_discounts.append(f"{discount.description}: -{discount.value}% (-${discount_value:.2f})")
            elif discount.rule_type == "fixed_amount":
                discount_amount += discount.value
                applied_discounts.append(f"{discount.description}: -${discount.value:.2f}")
            elif discount.rule_type == "buy_x_get_y":
                # Simple implementation for buy X get Y free
                conditions = discount.conditions or DiscountConditions()
                min_items = conditions.min_items or 2
                free_items = conditions.free_items or 1
                
                eligible_items = [item for item in items if item.category == (conditions.category or "food")]
                if len(eligible_items) >= min_items:
                    # Apply discount to cheapest items
                    eligible_items.sort(key=lambda x: x.unit_price)
                    for i in range(min(free_items, len(eligible_items))):
                        discount_amount += eligible_items[i].unit_price
                        applied_discounts.append(f"{discount.description}: Free {eligible_items[i].item_name}")
    
    # Calculate amounts after discount
    discounted_subtotal = subtotal - discount_amount
    service_charge = discounted_subtotal * service_charge_rate
    tax_amount = discounted_subtotal * tax_rate
    total_amount = discounted_subtotal + service_charge + tax_amount
    
    return ReceiptCalculation(
        subtotal=subtotal,
        discount_amount=discount_amount,
        applied_discounts=applied_discounts,
        service_charge=service_charge,
        tax_amount=tax_amount,
        total_amount=total_amount,
        message=f"Calculated total: ${total_amount:.2f} (Subtotal: ${subtotal:.2f}, Discounts: -${discount_amount:.2f}, Tax: ${tax_amount:.2f}, Service: ${service_charge:.2f})",
        success=True
    )


@function_tool
def generate_invoice(items: List[ReceiptItem], customer_name: str = None, room_number: int = None, 
                    check_in_date: str = None, check_out_date: str = None, 
                    tax_rate: float = 0.08, service_charge_rate: float = 0.10,
                    discounts: List[DiscountRule] = None) -> Invoice:
    """
    Generates a comprehensive invoice for hotel services.
    
    Args:
        items: List of items to include in the invoice
        customer_name: Name of the customer
        room_number: Room number if applicable
        check_in_date: Check-in date (YYYY-MM-DD format)
        check_out_date: Check-out date (YYYY-MM-DD format)
        tax_rate: Tax rate to apply
        service_charge_rate: Service charge rate to apply
        discounts: List of discount rules to apply
    """
    # Calculate totals
    calculation = calculate_receipt_total(items, tax_rate, service_charge_rate, discounts)
    
    # Generate unique invoice ID
    invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{hash(str(items)) % 10000:04d}"
    
    # Create invoice
    invoice = Invoice(
        invoice_id=invoice_id,
        customer_name=customer_name,
        room_number=room_number,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        items=items,
        subtotal=calculation.subtotal,
        discounts=calculation.applied_discounts,
        tax_rate=tax_rate,
        tax_amount=calculation.tax_amount,
        service_charge=calculation.service_charge,
        total_amount=calculation.total_amount,
        created_at=datetime.now().isoformat()
    )
    
    return invoice


@function_tool
def apply_discount_rules(items: List[ReceiptItem], discount_type: str, discount_value: float, 
                        conditions: DiscountConditions = None) -> DiscountResult:
    """
    Applies discount rules to a list of items and calculates the savings.
    
    Args:
        items: List of receipt items
        discount_type: Type of discount ("percentage", "fixed_amount", "buy_x_get_y", "room_stay")
        discount_value: Value of the discount
        conditions: Additional conditions for the discount
    """
    if not items:
        return DiscountResult(discount_amount=0.0, message="No items to apply discount", success=False)
    
    subtotal = sum(item.total_price for item in items)
    discount_amount = 0.0
    message = ""
    
    if discount_type == "percentage":
        if 0 <= discount_value <= 100:
            discount_amount = subtotal * (discount_value / 100)
            message = f"Applied {discount_value}% discount: -${discount_amount:.2f}"
        else:
            return DiscountResult(discount_amount=0.0, message="Invalid percentage value", success=False)
    
    elif discount_type == "fixed_amount":
        discount_amount = min(discount_value, subtotal)  # Don't discount more than total
        message = f"Applied fixed discount: -${discount_amount:.2f}"
    
    elif discount_type == "room_stay":
        # Discount based on length of stay
        conditions = conditions or DiscountConditions()
        nights = conditions.nights or 1
        if nights >= 3:
            discount_amount = subtotal * 0.10  # 10% for 3+ nights
            message = f"Long stay discount (3+ nights): -${discount_amount:.2f}"
        elif nights >= 7:
            discount_amount = subtotal * 0.15  # 15% for weekly stays
            message = f"Weekly stay discount: -${discount_amount:.2f}"
    
    elif discount_type == "buy_x_get_y":
        conditions = conditions or DiscountConditions()
        category = conditions.category or "food"
        min_items = conditions.min_items or 2
        
        eligible_items = [item for item in items if item.category == category]
        if len(eligible_items) >= min_items:
            # Give cheapest item free
            cheapest_item = min(eligible_items, key=lambda x: x.unit_price)
            discount_amount = cheapest_item.unit_price
            message = f"Buy {min_items} get 1 free: -{cheapest_item.item_name} (-${discount_amount:.2f})"
    
    return DiscountResult(
        discount_amount=discount_amount,
        message=message,
        success=True
    )


@function_tool
def calculate_stay_cost(room_number: int, price_per_night: float, check_in: str, check_out: str, 
                       room_service_items: List[ReceiptItem] = None) -> StayCostResult:
    """
    Calculates the total cost for a hotel stay including room and services.
    
    Args:
        room_number: Room number
        price_per_night: Price per night for the room
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        room_service_items: Additional room service items
    """
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        
        if check_out_date <= check_in_date:
            return StayCostResult(message="Check-out date must be after check-in date", success=False)
        
        nights = (check_out_date - check_in_date).days
        room_cost = nights * price_per_night
        
        # Add room service costs
        service_cost = 0.0
        if room_service_items:
            service_cost = sum(item.total_price for item in room_service_items)
        
        total_cost = room_cost + service_cost
        
        return StayCostResult(
            room_number=room_number,
            nights=nights,
            price_per_night=price_per_night,
            room_cost=room_cost,
            service_cost=service_cost,
            total_cost=total_cost,
            check_in=check_in,
            check_out=check_out,
            message=f"Room {room_number}: {nights} nights × ${price_per_night} = ${room_cost:.2f} + Services ${service_cost:.2f} = ${total_cost:.2f}",
            success=True
        )
    except ValueError:
        return StayCostResult(message="Invalid date format. Use YYYY-MM-DD", success=False)


@function_tool
def generate_payment_summary(invoices: List[Invoice]) -> PaymentSummary:
    """
    Generates a payment summary from multiple invoices for reporting.
    
    Args:
        invoices: List of invoices to summarize
    """
    if not invoices:
        return PaymentSummary(
            total_rooms_revenue=0.0,
            total_food_revenue=0.0,
            total_service_revenue=0.0,
            total_discounts=0.0,
            total_taxes=0.0,
            net_revenue=0.0,
            items_count=0,
            message="No invoices to summarize",
            success=False
        )
    
    total_rooms = 0.0
    total_food = 0.0
    total_service = 0.0
    total_discounts = 0.0
    total_taxes = 0.0
    items_count = 0
    
    for invoice in invoices:
        # Categorize revenue
        for item in invoice.items:
            items_count += item.quantity
            if item.category == "room":
                total_rooms += item.total_price
            elif item.category == "food":
                total_food += item.total_price
            else:
                total_service += item.total_price
        
        total_taxes += invoice.tax_amount
        if hasattr(invoice, 'discount_amount'):
            total_discounts += getattr(invoice, 'discount_amount', 0)
    
    gross_revenue = total_rooms + total_food + total_service
    net_revenue = gross_revenue - total_discounts + total_taxes
    
    return PaymentSummary(
        total_rooms_revenue=total_rooms,
        total_food_revenue=total_food,
        total_service_revenue=total_service,
        total_discounts=total_discounts,
        total_taxes=total_taxes,
        net_revenue=net_revenue,
        items_count=items_count,
        message=f"Summary: Gross Revenue ${gross_revenue:.2f}, Net Revenue ${net_revenue:.2f}, Total Items: {items_count}",
        success=True
    )


@function_tool
def convert_order_to_receipt_items(room_booking: RoomBookingInput = None, food_order: FoodOrderInput = None) -> List[ReceiptItem]:
    """
    Converts room bookings and food orders to receipt items for invoice generation.
    
    Args:
        room_booking: Room booking details from room agent
        food_order: Food order details from restaurant agent
    """
    receipt_items = []
    
    # Add room booking as receipt item
    if room_booking and room_booking.success:
        nights = room_booking.nights or 1
        total_cost = room_booking.total_cost or 0
        unit_price = total_cost / nights if nights > 0 else 0
        
        receipt_items.append(ReceiptItem(
            item_name=f"Room {room_booking.room_number or 'N/A'} - {room_booking.room_type or 'Standard'}",
            quantity=nights,
            unit_price=unit_price,
            total_price=total_cost,
            category="room",
            customizations=[f"Floor {room_booking.floor or 'N/A'}", f"{nights} nights"],
            special_instructions=f"Room {room_booking.room_number or 'N/A'}"
        ))
    
    # Add food items as receipt items
    if food_order and food_order.success and food_order.ordered_items:
        for item in food_order.ordered_items:
            receipt_items.append(ReceiptItem(
                item_name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                category="food",
                customizations=item.customizations_applied,
                special_instructions=item.special_instructions
            ))
    
    return receipt_items
