
import asyncio
import os
from dotenv import load_dotenv
from agents import Runner

from my_agents.orchestrator_agent import orchestrator_agent
from utils.db import HOTEL_ROOMS, RESTAURANT_MENU


async def main():
    """
    Main function to run the hotel management agent system.
    """
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable.")
        return

    print("Welcome to the Multi-Agent Hotel Management System!")
    print("You can ask to book a room, order from the restaurant, or both.")
    print("---------------------------------------------------------")
    print("Initial Room Availability:")
    for room in HOTEL_ROOMS:
        print(f"- Room {room['id']} ({room['type']}): {'Available' if room['available'] else 'Booked'}")
    print("---------------------------------------------------------")
    print("Initial Menu Availability:")
    for item in RESTAURANT_MENU:
        print(f"- {item['name']}: {'Available' if item['available'] else 'Not Available'}")
    print("---------------------------------------------------------")

    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        
        # Run the orchestrator agent with the user's query
        result = await Runner.run(orchestrator_agent, user_query)
        
        print(f"System: {result}")
        print("---------------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
