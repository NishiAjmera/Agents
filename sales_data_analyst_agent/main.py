from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uvicorn

# from pprint import pformat
from agent import root_agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Global session service and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent, app_name="social_media_assistant", session_service=session_service
)

sessions_store = {}


class AgentRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    responses: List[str]
    session_id: str
    user_id: str


@app.post("/chat")
async def chat(request: AgentRequest):
    """
    Endpoint to interact with the sales data analyst agent.
    """
    """
       Chat with the social media agent
       """
    try:
        # Get or create session
        session_key = (
            f"{request.user_id}_{request.session_id}"
            if request.session_id
            else request.user_id
        )

        # if session_key not in sessions_store:
        session = await session_service.create_session(
            app_name="social_media_assistant",
            user_id=request.user_id,
            session_id=request.session_id,
        )
        sessions_store[session_key] = session
        # else:
        #     session = sessions_store[session_key]

        # Process the message
        events_iterator = runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=request.message)]
            ),
        )

        responses = []
        final_response_text = ""

        async for event in events_iterator:
            # if event.content and event.content.parts:
            #     for part in event.content.parts:
            #         if part.function_call:
            #             formatted_call = f"Function Call - {part.function_call.name}:\n{pformat(part.function_call.model_dump(), indent=2, width=80)}"
            #             responses.append(formatted_call)
            #         elif part.function_response:
            #             formatted_response = f"Function Response:\n{pformat(part.function_response.model_dump(), indent=2, width=80)}"
            #             responses.append(formatted_response)

            # Handle final response
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                else:
                    final_response_text = "No response content available."

                responses.append(final_response_text)
                break

        return AgentResponse(
            responses=responses, session_id=session.id, user_id=request.user_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
