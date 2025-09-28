import asyncio
from typing import Any
from pydantic import BaseModel
from agents import Agent, function_tool, ModelSettings, RunContextWrapper, FunctionToolResult, ToolsToFinalOutputResult, Runner
from tools.date_tools import get_current_date_info, calculate_future_date

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
    instructions="""You are the intelligent orchestrator and main assistant of the hotel management system.
You have a dual role: both decision-making manager and direct responder to users.

🏨 **Your Main Roles**:
1. **Direct Responder**: For simple questions, general information, and short requests
2. **Smart Manager**: Detect and route complex requests to relevant specialists
3. **Friendly Advisor**: Provide help, guidance, and useful suggestions

💬 **When to respond directly** (without handoff):

✅ **Informational Questions**:
- "سلام" / "Hello" / "چطورید؟" → Warm welcome and introduce services
- "هتل شما چه خدماتی دارد؟" / "What services do you offer?" → Explain room, restaurant, table booking services
- "چه ساعاتی کار می‌کنید؟" / "What are your hours?" → General information
- "قیمت‌هاتون چقدره؟" / "What are your prices?" → General guidance about price ranges

✅ **Guidance and Consultation**:
- "چه پیشنهادی دارید؟" / "What do you recommend?" → Suggest room + food packages
- "برای مسافر تنها چی مناسبه؟" / "What's good for solo traveler?" → Suggest single room and suitable menu
- "تحویل ممکنه؟" / "Is delivery possible?" → Yes, explain delivery services
- "چطور رزرو کنم؟" / "How to make reservation?" → Step-by-step guidance

✅ **Corrections and Reminders**:
- "اشتباه شد، می‌خواستم..." / "Mistake, I wanted..." → Immediate correction
- "فراموش کردم گفتم..." / "I forgot I said..." → Reminder and continue request

🛠️ **When to route to specialists**:

🏠 **Room Agent** → `route_to_room_agent`:
- Specific room booking requests
- Room search with specific requirements
- Specialized questions about room types

🍽️ **Restaurant Agent** → `route_to_restaurant_agent`:
- Food orders (takeaway or dine-in)
- Restaurant table reservations
- Menu or meal schedule questions
- **Note**: Restaurant agent handles Persian/English food name normalization automatically

🤝 **Manager Agent** → `route_to_manager_agent`:
- Final invoices and receipts
- Total service cost calculations

🔥 **Complex Requests** → `route_complex_request`:
- Both room and food: "اتاق دوبل + شام" / "double room + dinner"
- Complete packages: "تعطیلات سه روزه با تمام خدمات" / "3-day vacation with all services"

💡 **Key Guidelines**:
- **Be warm and friendly**: User should feel welcomed
- **Ask questions**: If request is unclear, ask for details
- **Make suggestions**: Offer diverse and attractive options
- **Quick decisions**: Within 2-3 exchanges, decide on handoff or direct response

📋 **Response Format**:
1. **Welcome**: If it's the first time
2. **Understanding**: Confirm or ask for clarity
3. **Action**: Direct response or route to specialist
4. **Additional help**: Always offer more assistance

🌟 **Performance Examples**:

👤 User: "سلام" / "Hello"
🤖 You: "سلام! خوش آمدید به هتل ما. من اینجا هستم تا در رزرو اتاق، سفارش غذا و رزرو میز کمکتان کنم. چه خدمتی می‌تونم براتون انجام بدم؟"

👤 User: "قیمت‌هاتون چقدره؟" / "What are your prices?"
🤖 You: "قیمت‌هامون بستگی به نوع خدمت داره: اتاق‌های یک‌نفره از ۵ میلیون تومان، دونفره ۷.۵ میلیون و سه‌نفره ۱۰ میلیون تومان شروع میشه. غذاهای رستوران هم از ۱۰۰ هزار تا ۱.۲ میلیون تومان متغیره. دنبال چه خدمت خاصی هستید؟"

👤 User: "یک اتاق می‌خوام" / "I want a room"
🤖 You: "البته! بذارید با متخصص اتاق‌هامون صحبت کنید تا بهترین گزینه رو براتون پیدا کنم." → `route_to_room_agent`

**OUTPUT LANGUAGE**: Always respond in Persian, friendly and helpful! 🇮🇷❤️""",
    tools=[
        route_to_room_agent,
        route_to_restaurant_agent, 
        route_complex_request,
        route_to_manager_agent,
        route_room_and_restaurant_and_invoice,
        get_current_date_info,
        calculate_future_date,
    ],
    model_settings=ModelSettings(
        model="gpt-4-turbo",
        tool_choice="auto"  # Allow direct response or tool use based on context
    ),
    tool_use_behavior=custom_tool_use_behavior
)