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
async def route_room_and_restaurant_and_invoice(room_query: str, food_query: str) -> RouteResponse:
    """
    Runs room and restaurant agents in parallel, then consolidates via manager agent.
    This is the most efficient option for combined requests.

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
            result=f"Error processing parallel request: {str(e)}",
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
    instructions="""You are the orchestrator for a hotel management system.
Your job is to analyze the user's request and route it to the appropriate specialized agent or agents.

- For room-only requests, use `route_to_room_agent`.
- For food-only requests, use `route_to_restaurant_agent`.
- For combined room and food requests, prefer `route_room_and_restaurant_and_invoice` as it runs both agents in parallel for efficiency and then produces a consolidated invoice.
- Only use `route_to_manager_agent` if you already have separate results from room and restaurant agents.

Always choose the most efficient routing option based on the user's request.""",
    tools=[
        route_to_room_agent,
        route_to_restaurant_agent,
        route_to_manager_agent,
        route_room_and_restaurant_and_invoice,
    ],
    model_settings=ModelSettings(
        model="gpt-4-turbo",
        tool_choice="required"  # Force tool use as per the example
    ),
    tool_use_behavior=custom_tool_use_behavior
)