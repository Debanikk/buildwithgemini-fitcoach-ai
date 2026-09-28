# Copyright 2026 Google LLC
# FitCoach AI Root Agent definition with Firestore tools.

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_custom_exercise,
    calculate_training_zones,
    find_nearby_places,
    generate_exercise_image,
    generate_exercise_video,
    geocode_address,
    get_exercise_catalog,
    log_user_workout,
    search_public_exercise_db,
)


FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-675a8fdff8e3"
LOCATION = "us-east1"

# Load Agent Engine resource name from deployment_metadata.json
deployment_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
agent_engine_id = None
if deployment_metadata_path.exists():
    try:
        with open(deployment_metadata_path) as f:
            meta = json.load(f)
        agent_engine_id = meta.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_id
)

# Extract Memory Bank ID from remote_agent_runtime_id if present
MEMORY_BANK_ID = agent_engine_id.split("/")[-1] if agent_engine_id else "1037153925318311936"


def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project=FIRESTORE_PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


memory_service = memory_bank_service_builder()


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


def get_current_time(query: str = "local") -> str:
    """Gets the current time.

    Args:
        query: Location or timezone query string.

    Returns:
        Formatted string with current time.
    """
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.datetime.now(tz)
    return f"The current time is {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


# A2UI Schema Manager setup for Version 0.8 and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FitCoach AI, an intelligent fitness and workout assistant. "
        "Pay special attention to user health details—including current medications, "
        "past surgeries, chronic health issues, joint/cardiovascular conditions, and physical limitations. "
        "Consistently remember these medical facts and health conditions across sessions via Memory Bank, "
        "and ensure every workout recommendation and training plan strictly respects them to keep the user safe. "
        "Help users explore exercises from Firestore or the public exercise database, "
        "add custom exercises, calculate training zones, geocode locations, find nearby gyms/parks, "
        "generate visual exercise illustrations, execute Python code for complex calculations, "
        "and log completed workouts. Be motivating, empathetic, precise, and supportive!"
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        get_exercise_catalog,
        add_custom_exercise,
        log_user_workout,
        calculate_training_zones,
        search_public_exercise_db,
        geocode_address,
        find_nearby_places,
        generate_exercise_image,
        generate_exercise_video,
        get_current_time,
    ],

)

app = App(
    root_agent=root_agent,
    name="app",
)
