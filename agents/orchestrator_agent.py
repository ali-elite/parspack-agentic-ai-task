import asyncio
from agents import Agent, tool

from my_agents.room_agent import room_agent
from my_agents.restaurant_agent import restaurant_agent
from my_agents.manager_agent import manager_agent

@tool
async def route_to_room_agent(query: str):
    """
    Routes a user's query to the room booking agent.
    Use this for all requests related to booking or checking availability of hotel rooms.
    
    Args:
        query (str): The user's request about room booking.
    """
    return await room_agent.run(query)

@tool
async def route_to_restaurant_agent(query: str):
    """
    Routes a user's query to the restaurant agent.
    Use this for all requests related to ordering food or asking about the menu.
    
    Args:
        query (str): The user's request about food ordering.
    """
    return await restaurant_agent.run(query)

@tool
async def route_to_manager_agent(room_result: str, food_result: str):
    """
    Routes the results from the room and restaurant agents to the hotel manager for final processing.
    Use this when a user's request involves both room booking and food ordering.
    
    Args:
        room_result (str): The result from the room booking agent.
        food_result (str): The result from the restaurant agent.
    """
    combined_results = f"Room Booking Details: {room_result}\n\nFood Order Details: {food_result}"
    return await manager_agent.run(combined_results)

@tool
async def route_room_and_restaurant_and_invoice(room_query: str, food_query: str):
    """
    Runs room and restaurant agents in parallel, then consolidates via manager agent.

    Args:
        room_query (str): Natural language request for room booking.
        food_query (str): Natural language request for restaurant ordering.
    """
    room_task = asyncio.create_task(room_agent.run(room_query))
    food_task = asyncio.create_task(restaurant_agent.run(food_query))
    room_result, food_result = await asyncio.gather(room_task, food_task)

    combined_results = f"Room Booking Details: {room_result}\n\nFood Order Details: {food_result}"
    return await manager_agent.run(combined_results)

orchestrator_agent = Agent(
    model="gpt-4-turbo-preview",
    system_prompt="""You are the orchestrator for a hotel management system.
Your job is to analyze the user's request and route it to the appropriate specialized agent or agents.
- For room-only requests, use `route_to_room_agent`.
- For food-only requests, use `route_to_restaurant_agent`.
- For combined room and food requests, you must first call the room and restaurant agents separately,
  then use `route_to_manager_agent` with the combined results to generate a final invoice.

Prefer `route_room_and_restaurant_and_invoice` when the user clearly has both a room and food request; it will perform the sub-tasks in parallel for efficiency and then produce a consolidated invoice.""",
    tools=[
        route_to_room_agent,
        route_to_restaurant_agent,
        route_to_manager_agent,
        route_room_and_restaurant_and_invoice,
    ]
)
