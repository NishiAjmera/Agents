import os
from google.adk.agents import Agent
from dotenv import load_dotenv
from tools import log_habit, get_summary

load_dotenv()

# Configure the Gemini API key from environment variables
# Ensure GOOGLE_API_KEY is set in your .env file or environment
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

habit_tracker_agent = Agent(
    name="habit_tracker_agent",
    model="gemini-2.5-flash",
    description="A friendly wellness coach that helps users log daily habits and summarize their activity.",
    instruction=(
        "You are a friendly wellness coach. "
        "Your goal is to help users log their daily habits like workouts, meals, water intake, or steps. "
        "When a user logs a habit, respond with encouragement. "
        "You can also provide a summary of their logged habits over a specified period (e.g., daily, weekly). "
        "Use the tools provided to log habits and retrieve summaries."
    ),
    tools=[log_habit, get_summary],
)
