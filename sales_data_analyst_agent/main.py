from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.protobuf.json_format import MessageToDict
from google.genai import types
import uvicorn
import shutil
import tempfile

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


# class AgentRequest(BaseModel):
#     message: Optional[str] = None
#     user_id: Optional[str] = "default_user"
#     session_id: Optional[str] = None


class AgentResponse(BaseModel):
    responses: List[str]
    session_id: str
    user_id: str
    visualization: Optional[Dict[str, Any]] = None


@app.post("/chat")
async def chat(
    file: UploadFile = File(...),
    message: Optional[str] = Form(None),
    user_id: Optional[str] = Form("default_user"),
    session_id: Optional[str] = Form(None),
):
    """
    Endpoint to interact with the sales data analyst agent.
    """
    """
       Chat with the social media agent
       """
    try:
        # Get or create session
        session_key = f"{user_id}_{session_id}" if session_id else user_id

        # if session_key not in sessions_store:
        session = await session_service.create_session(
            app_name="social_media_assistant",
            user_id=user_id,
            session_id=session_id,
        )
        sessions_store[session_key] = session
        # else:
        #     session = sessions_store[session_key]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Process the message
        events_iterator = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=f"read_csv_and_get_schema(file_path='{tmp_path}')\n{message or ''}"
                    )
                ],
            ),
        )

        responses = []
        final_response_text = ""
        visualization_data = None

        async for event in events_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if (
                        part.function_response
                        and part.function_response.name == "generate_visualization_data"
                    ):
                        # Access response directly - it should be a dict or dict-like object
                        tool_output = part.function_response.response

                        # Handle if it's already a dict
                        if isinstance(tool_output, dict):
                            if (
                                tool_output.get("status") == "success"
                                and "visualization" in tool_output
                            ):
                                visualization_data = tool_output["visualization"]

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
            responses=responses,
            session_id=session.id,
            user_id=user_id,
            visualization=visualization_data,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
    finally:
        file.file.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
