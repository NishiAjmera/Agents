from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uvicorn
import logging
from agent import habit_tracker_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # React frontend
    "http://localhost:3001",  # Alternative port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session service
session_service = InMemorySessionService()

# Initialize runner
runner = Runner(
    agent=habit_tracker_agent,
    app_name="habit_tracker_app",
    session_service=session_service,
)


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint to interact with the habit tracker agent.
    Manages conversation state using sessions.
    """
    try:
        logger.info(f"Received chat request: {request.message}")

        # Get or create session
        session_id = None

        if not session_id:
            # Create new session
            logger.info(f"Creating new session for user: user-1")
            session = await session_service.create_session(
                app_name="habit_tracker_app", user_id="user-1"
            )
            session_id = session.id
        # logger.info(f"Using session ID: {session.id}")
        logger.info(f"Using session_ID: {session_id}")

        # Run the agent with the message
        events_iterator = runner.run_async(
            session_id=session_id,
            user_id="user-1",
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=request.message)],
            ),
        )

        final_response_text = ""

        # Collect all events and extract the response
        async for event in events_iterator:
            logger.info(f"Event type: {type(event).__name__}")

            # Check different event types for the response
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts") and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            # Only update if it's from the model (not echoing user input)
                            if (
                                hasattr(event.content, "role")
                                and event.content.role == "model"
                            ):
                                final_response_text = part.text
                                logger.info(
                                    f"Found model response: {final_response_text[:100]}..."
                                )

        if not final_response_text:
            final_response_text = "Sorry, I couldn't process that. Please try again."
            logger.warning("No response found from model")

        return ChatResponse(response=final_response_text, session_id=session_id)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Habit Tracker Agent API", "status": "running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
