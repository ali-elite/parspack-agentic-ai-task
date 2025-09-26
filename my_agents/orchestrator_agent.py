import asyncio
from typing import Any
from pydantic import BaseModel
from agents import Agent, function_tool, ModelSettings, RunContextWrapper, FunctionToolResult, ToolsToFinalOutputResult, Runner

from my_agents.room_agent import room_agent
from my_agents.restaurant_agent import restaurant_agent
from my_agents.manager_agent import manager_agent


class RouteResponse(BaseModel):
    result: str
    agent_used: str
    success: bool


@function_tool
async def route_to_room_agent(query: str) -> RouteResponse:
    """
    Routes a user's query to the room booking agent.
    Use this for all requests related to booking or checking availability of hotel rooms.
    
    Args:
        query: The user's request about room booking.
    """
    try:
        result = await Runner.run(room_agent, query)
        return RouteResponse(
            result=str(result),
            agent_used="room_agent",
            success=True
        )
    except Exception as e:
        return RouteResponse(
            result=f"Error processing room request: {str(e)}",
            agent_used="room_agent",
            success=False
        )


@function_tool
async def route_to_restaurant_agent(query: str) -> RouteResponse:
    """
    Routes a user's query to the restaurant agent.
    Use this for all requests related to ordering food or asking about the menu.
    
    Args:
        query: The user's request about food ordering.
    """
    try:
        result = await Runner.run(restaurant_agent, query)
        return RouteResponse(
            result=str(result),
            agent_used="restaurant_agent",
            success=True
        )
    except Exception as e:
        return RouteResponse(
            result=f"Error processing restaurant request: {str(e)}",
            agent_used="restaurant_agent",
            success=False
        )


@function_tool
async def route_to_manager_agent(room_result: str, food_result: str) -> RouteResponse:
    """
    Routes the results from the room and restaurant agents to the hotel manager for final processing.
    Use this when a user's request involves both room booking and food ordering.
    
    Args:
        room_result: The result from the room booking agent.
        food_result: The result from the restaurant agent.
    """
    try:
        combined_results = f"Room Booking Details: {room_result}\n\nFood Order Details: {food_result}"
        result = await Runner.run(manager_agent, combined_results)
        return RouteResponse(
            result=str(result),
            agent_used="manager_agent",
            success=True
        )
    except Exception as e:
        return RouteResponse(
            result=f"Error processing combined request: {str(e)}",
            agent_used="manager_agent",
            success=False
        )


@function_tool
async def route_complex_request(full_query: str) -> RouteResponse:
    """
    Handles complex requests that involve both room and food services automatically.
    This function intelligently processes the full request, routing to both room and restaurant agents,
    then consolidates the results through the manager agent.
    
    Use this for ANY request that mentions both accommodation/room AND food/restaurant services,
    regardless of how complex or intertwined the request might be.

    Args:
        full_query: The complete user request containing both room and food elements.
    """
    try:
        # Run both agents in parallel with the full query
        # Each agent will extract what's relevant to them from the full request
        room_task = asyncio.create_task(Runner.run(room_agent, full_query))
        food_task = asyncio.create_task(Runner.run(restaurant_agent, full_query))
        room_result, food_result = await asyncio.gather(room_task, food_task)

        # Consolidate via manager with clear context
        combined_context = f"""
درخواست اصلی مشتری: {full_query}

نتایج رزرو اتاق: {str(room_result)}

نتایج سفارش غذا: {str(food_result)}

لطفاً یک فاکتور جامع و حرفه‌ای تهیه کنید که هر دو خدمت را شامل شود."""

        final_result = await Runner.run(manager_agent, combined_context)
        
        return RouteResponse(
            result=str(final_result),
            agent_used="complex_request_handler",
            success=True
        )
    except Exception as e:
        return RouteResponse(
            result=f"خطا در پردازش درخواست پیچیده: {str(e)}",
            agent_used="complex_request_handler",
            success=False
        )


@function_tool  
async def route_room_and_restaurant_and_invoice(room_query: str, food_query: str) -> RouteResponse:
    """
    DEPRECATED: Use route_complex_request instead.
    This function is kept for backward compatibility but route_complex_request is preferred.
    
    Runs room and restaurant agents in parallel with separate queries, then consolidates via manager agent.

    Args:
        room_query: Natural language request for room booking.
        food_query: Natural language request for restaurant ordering.
    """
    try:
        # Run both agents in parallel
        room_task = asyncio.create_task(Runner.run(room_agent, room_query))
        food_task = asyncio.create_task(Runner.run(restaurant_agent, food_query))
        room_result, food_result = await asyncio.gather(room_task, food_task)

        # Consolidate via manager
        combined_results = f"Room Booking Details: {str(room_result)}\n\nFood Order Details: {str(food_result)}"
        final_result = await Runner.run(manager_agent, combined_results)
        
        return RouteResponse(
            result=str(final_result),
            agent_used="parallel_room_restaurant_manager", 
            success=True
        )
    except Exception as e:
        return RouteResponse(
            result=f"خطا در پردازش درخواست موازی: {str(e)}",
            agent_used="parallel_room_restaurant_manager",
            success=False
        )


async def custom_tool_use_behavior(
    context: RunContextWrapper[Any], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    """
    Custom tool use behavior that formats the response from routing tools.
    """
    if not results:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output="No routing result available."
        )
    
    route_response: RouteResponse = results[0].output
    
    if route_response.success:
        final_output = route_response.result
    else:
        final_output = f"❌ {route_response.result}"
    
    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=final_output
    )


orchestrator_agent = Agent(
    name="Hotel Orchestrator",
    instructions="""شما ارکستراتور هوشمند سیستم مدیریت هتل هستید.
وظیفه شما تحلیل دقیق درخواست کاربر و هدایت آن به بهترین مسیر پردازش است.

💬 **مدیریت مکالمه**: 
- شما می‌تواید تاریخچه گفتگو دریافت کنید که شامل پیام‌های قبلی کاربر و پاسخ‌های سیستم است
- در صورت وجود تاریخچه، به آن توجه کنید تا پاسخ‌های مرتبط و مناسب ارائه دهید
- اگر کاربر به چیزی که قبلاً گفته یا درخواست کرده اشاره می‌کند، از تاریخچه استفاده کنید
- برای سؤالات تکمیلی یا تغییرات، زمینه قبلی را در نظر بگیرید

🎯 راهنمای تصمیم‌گیری:

1️⃣ **درخواست‌های ساده اتاق**: اگر فقط درباره رزرو، بررسی موجودی، یا سؤال درباره اتاق‌ها است
   ➡️ از `route_to_room_agent` استفاده کنید

2️⃣ **درخواست‌های ساده غذا**: اگر فقط درباره سفارش غذا، منو، یا خدمات رستوران است  
   ➡️ از `route_to_restaurant_agent` استفاده کنید

3️⃣ **درخواست‌های پیچیده ترکیبی**: اگر درخواست شامل هر دو موضوع اتاق و غذا است
   ➡️ از `route_complex_request` استفاده کنید (بهترین گزینه!)
   
مثال‌های درخواست پیچیده:
- "یک اتاق دوبل می‌خواهم و برای شام هم پیتزا سفارش دهید"
- "اتاق سه نفره برای دو شب + ناهار و شام"
- "رزرو اتاق + سفارش غذا برای مهمانی"
- هر درخواستی که هم اتاق و هم غذا را ذکر کند

4️⃣ **فقط برای موارد خاص**: `route_to_manager_agent` تنها زمانی که نتایج جداگانه از قبل دارید

🔥 **مهم**: برای درخواست‌های پیچیده، حتماً کل متن درخواست را به `route_complex_request` بدهید، نیازی به تقسیم متن نیست!

📝 **مدیریت follow-up**: اگر کاربر سؤال تکمیلی یا تغییری در درخواست قبلی دارد، کل زمینه (درخواست اصلی + تغییرات جدید) را به agent مربوطه ارسال کنید.

پاسخ‌های نهایی همیشه به زبان فارسی و با لحن حرفه‌ای باشند.""",
    tools=[
        route_to_room_agent,
        route_to_restaurant_agent, 
        route_complex_request,
        route_to_manager_agent,
        route_room_and_restaurant_and_invoice,
    ],
    model_settings=ModelSettings(
        model="gpt-4-turbo",
        tool_choice="required"  # Force tool use as per the example
    ),
    tool_use_behavior=custom_tool_use_behavior
)