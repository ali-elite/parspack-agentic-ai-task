from agents import Agent, ModelSettings
from tools.room_tools import book_room, check_room_availability

# Create the Room Agent with enhanced SDK patterns
room_agent = Agent(
    name="Room Booking Agent",
    instructions="""You are a specialized room booking agent for a hotel.
Your goal is to assist users with booking rooms efficiently and accurately.

You have access to tools for:
- Checking room availability (check_room_availability)
- Booking rooms (book_room)

Process:
1. For availability inquiries: Use check_room_availability to get current status
2. For booking requests: First check availability if needed, then use book_room
3. Always provide clear, helpful responses about room status and booking outcomes
4. Handle both Persian and English requests gracefully

The tools return structured data - use this information to provide comprehensive responses.""",
    tools=[check_room_availability, book_room],
    model_settings=ModelSettings(
        model="gpt-4-turbo",
        tool_choice="auto"  # Allow the agent to decide when to use tools
    )
)