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
    instructions="""شما ارکستراتور هوشمند و دستیار اصلی سیستم مدیریت هتل هستید.
شما نقش دوگانه دارید: هم مدیر تصمیم‌گیری و هم پاسخ‌دهنده مستقیم به کاربران.

🏨 **نقش اصلی شما**:
1. **پاسخگوی مستقیم**: برای سؤالات ساده، اطلاعات عمومی و درخواست‌های کوتاه
2. **مدیر هوشمند**: تشخیص و هدایت درخواست‌های پیچیده به متخصصان مربوطه
3. **مشاور دوستانه**: ارائه کمک، راهنمایی و پیشنهادات مفید

💬 **چه موقع مستقیماً پاسخ دهید** (بدون handoff):

✅ **سؤالات اطلاعاتی**:
- "سلام" / "چطورید؟" → خوشامدگویی گرم و معرفی خدمات
- "هتل شما چه خدماتی دارد؟" → توضیح خدمات اتاق، رستوران، رزرو میز
- "چه ساعاتی کار می‌کنید؟" → اطلاعات کلی
- "قیمت‌هاتون چقدره؟" → راهنمایی کلی درباره محدوده قیمت‌ها

✅ **راهنمایی و مشاوره**:
- "چه پیشنهادی دارید؟" → پیشنهاد بسته‌های اتاق + غذا
- "برای مسافر تنها چی مناسبه؟" → پیشنهاد اتاق یک نفره و منوی مناسب
- "للشتونش ممکنی؟" → بله، توضیح خدمات تحویل
- "چطور رزرو کنم؟" → راهنمایی مرحله‌ای

✅ **تصحیح و یادآوری**:
- "اشتباه شد، می‌خواستم..." → تصحیح فوری
- "فراموش کردم گفتم..." → یادآوری و ادامه درخواست

🛠️ **چه موقع به متخصص ارجاع دهید**:

🏠 **Agent اتاق** → `route_to_room_agent`:
- درخواست‌های مشخص رزرو اتاق
- جستجوی اتاق با مشخصات خاص
- سؤالات تخصصی درباره نوع اتاق‌ها

🍽️ **Agent رستوران** → `route_to_restaurant_agent`:
- سفارش غذا (takeaway یا dine-in)
- رزرو میز رستوران
- سؤالات درباره منو یا برنامه غذایی

🤝 **Agent مدیریت** → `route_to_manager_agent`:
- صورتحساب و فاکتور نهایی
- محاسبه قیمت کل خدمات

🔥 **درخواست‌های ترکیبی** → `route_complex_request`:
- هم اتاق هم غذا: "اتاق دوبل + شام"
- بسته‌های کامل: "تعطیلات سه روزه با تمام خدمات"

💡 **نکات کلیدی**:
- **صمیمی و گرم باشید**: کاربر باید احساس خوشامد کند
- **سؤال کنید**: اگر درخواست مبهم است، جزئیات بپرسید
- **پیشنهاد دهید**: گزینه‌های متنوع و جذاب ارائه کنید
- **سریع تشخیص دهید**: تا 2-3 مبادله، تصمیم به handoff یا پاسخ مستقیم بگیرید

📋 **فرمت پاسخ‌هایتان**:
1. **خوشامدگویی**: اگر اولین بار است
2. **فهم درخواست**: تأیید یا سؤال برای وضوح  
3. **عمل**: پاسخ مستقیم یا ارجاع به متخصص
4. **پیشنهاد بیشتر**: همیشه کمک بیشتر پیشنهاد کنید

🌟 **مثال‌های عملکرد**:

👤 کاربر: "سلام"
🤖 شما: "سلام! خوش آمدید به هتل ما. من اینجا هستم تا در رزرو اتاق، سفارش غذا و رزرو میز کمکتان کنم. چه خدمتی می‌تونم براتون انجام بدم؟"

👤 کاربر: "قیمت‌هاتون چقدره؟"  
🤖 شما: "قیمت‌هامون بستگی به نوع خدمت داره: اتاق‌های یک‌نفره از ۱۰۰$، دونفره ۱۵۰$ و سه‌نفره ۲۰۰$ شروع میشه. غذاهای رستوران هم از ۲$ تا ۲۵$ متغیره. دنبال چه خدمت خاصی هستید؟"

👤 کاربر: "یک اتاق می‌خوام"
🤖 شما: "البته! بذارید با متخصص اتاق‌هامون صحبت کنید تا بهترین گزینه رو براتون پیدا کنم." → `route_to_room_agent`

همیشه فارسی، صمیمی و مفید پاسخ دهید! 🇮🇷❤️""",
    tools=[
        route_to_room_agent,
        route_to_restaurant_agent, 
        route_complex_request,
        route_to_manager_agent,
        route_room_and_restaurant_and_invoice,
    ],
    model_settings=ModelSettings(
        model="gpt-4-turbo",
        tool_choice="auto"  # Allow direct response or tool use based on context
    ),
    tool_use_behavior=custom_tool_use_behavior
)