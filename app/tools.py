# Copyright 2026 Google LLC
# Firestore tools for FitCoach AI

import datetime
from typing import Optional
from google.cloud import firestore
from google.adk.tools import ToolContext

# Hardcode project ID explicitly as required for Agent Platform runtime compatibility
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-675a8fdff8e3"
GCS_ASSETS_BUCKET_NAME = "fitcoach-ai-assets-qwiklabs-gcp-03-675a8fdff8e3"


def _get_db() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def get_exercise_catalog(muscle_group: Optional[str] = None) -> list[dict]:
    """Retrieves exercises from the Firestore exercise catalog.

    Args:
        muscle_group: Optional filter by target muscle group (e.g. 'Legs', 'Chest', 'Back', 'Cardio').

    Returns:
        List of exercise dictionaries containing id, name, muscle_group, difficulty, description, and recommended_reps.
    """
    db = _get_db()
    docs = db.collection("exercises").stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        if muscle_group:
            data_muscle = str(data.get("muscle_group", "")).lower()
            if muscle_group.lower() not in data_muscle:
                continue
        results.append(data)
    
    return results


def add_custom_exercise(
    name: str,
    muscle_group: str,
    difficulty: str,
    description: str,
    recommended_reps: str,
) -> str:
    """Adds a new custom exercise to the Firestore exercise catalog.

    Args:
        name: Name of the exercise (e.g. 'Dumbbell Bicep Curls').
        muscle_group: Target muscle group (e.g. 'Arms', 'Legs', 'Core').
        difficulty: Difficulty level ('Beginner', 'Intermediate', 'Advanced').
        description: Description of movement and technique.
        recommended_reps: Recommended sets and rep count (e.g. '3 sets of 12 reps').

    Returns:
        Confirmation message with the new exercise ID.
    """
    db = _get_db()
    ex_id = f"ex-{int(datetime.datetime.now().timestamp())}"
    exercise_doc = {
        "id": ex_id,
        "name": name,
        "muscle_group": muscle_group,
        "difficulty": difficulty,
        "description": description,
        "recommended_reps": recommended_reps,
    }
    db.collection("exercises").document(ex_id).set(exercise_doc)
    return f"Successfully added custom exercise '{name}' with ID '{ex_id}'."


def log_user_workout(exercise_name: str, sets: int, reps: int, notes: str = "") -> str:
    """Logs a completed exercise workout session into Firestore.

    Args:
        exercise_name: Name of the exercise performed.
        sets: Number of completed sets.
        reps: Number of repetitions per set.
        notes: Optional user notes or weight lifted.

    Returns:
        Confirmation message for the logged workout.
    """
    db = _get_db()
    log_id = f"log-{int(datetime.datetime.now().timestamp())}"
    log_doc = {
        "log_id": log_id,
        "exercise_name": exercise_name,
        "sets": sets,
        "reps": reps,
        "notes": notes,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection("workout_logs").document(log_id).set(log_doc)
    return f"Successfully logged workout for '{exercise_name}' ({sets} sets of {reps} reps)."


def calculate_training_zones(age: int, resting_heart_rate: int = 60) -> dict:
    """Calculates target heart rate training zones using the Karvonen formula.

    Args:
        age: Age of the user in years.
        resting_heart_rate: Resting heart rate in BPM (beats per minute), default is 60.

    Returns:
        Dictionary containing max heart rate, heart rate reserve, and heart rate ranges for Fat Burn (60-70%), Aerobic (70-80%), and Anaerobic/Threshold (80-90%) zones.
    """
    max_hr = 220 - age
    hrr = max_hr - resting_heart_rate

    fat_burn_low = int(resting_heart_rate + (hrr * 0.60))
    fat_burn_high = int(resting_heart_rate + (hrr * 0.70))

    aerobic_low = int(resting_heart_rate + (hrr * 0.70))
    aerobic_high = int(resting_heart_rate + (hrr * 0.80))

    threshold_low = int(resting_heart_rate + (hrr * 0.80))
    threshold_high = int(resting_heart_rate + (hrr * 0.90))

    return {
        "max_heart_rate_bpm": max_hr,
        "resting_heart_rate_bpm": resting_heart_rate,
        "fat_burn_zone_bpm": f"{fat_burn_low} - {fat_burn_high} BPM",
        "aerobic_cardio_zone_bpm": f"{aerobic_low} - {aerobic_high} BPM",
        "anaerobic_threshold_zone_bpm": f"{threshold_low} - {threshold_high} BPM",
    }


def search_public_exercise_db(query: str = "") -> list[dict]:
    """Queries the free public Wger Workout & Exercise Database for live exercise details.

    Args:
        query: Optional search keyword to filter exercises (e.g. 'Kettlebell', 'Bench', 'Squat').

    Returns:
        List of exercise dictionaries containing name, category, muscles, equipment, and description instructions.
    """
    import json
    import os
    import urllib.request

    url = "https://wger.de/api/v2/exerciseinfo/?limit=20&language=2"
    headers = {"User-Agent": "FitCoachAI/1.0", "Accept": "application/json"}

    api_key = os.environ.get("WGER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Token {api_key}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for item in data.get("results", []):
                translations = item.get("translations", [])
                name = ""
                description = ""
                for t in translations:
                    if t.get("language") == 2 or not name:
                        name = t.get("name", "")
                        description = t.get("description", "").replace("<p>", "").replace("</p>", "").strip()

                if not name:
                    continue

                if query and query.lower() not in name.lower() and query.lower() not in description.lower():
                    continue

                category = item.get("category", {}).get("name", "General")
                muscles = [m.get("name_en", m.get("name", "")) for m in item.get("muscles", [])]
                equipment = [e.get("name", "") for e in item.get("equipment", [])]

                results.append({
                    "name": name,
                    "category": category,
                    "muscles_worked": muscles,
                    "equipment_needed": equipment,
                    "instructions": description,
                })

                if len(results) >= 5:
                    break
            return results
    except Exception as e:
        return [{"error": f"Failed to fetch public exercise data: {e}"}]


def geocode_address(address: str) -> dict:
    """Converts a street address into latitude and longitude coordinates using the Google Maps Geocoding API.

    Args:
        address: Street address or city name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'New York, NY').

    Returns:
        Dictionary containing formatted_address, latitude, and longitude.
    """
    import json
    import os
    import urllib.parse
    import urllib.request
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY not configured in environment."}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "OK" and data.get("results"):
                top_result = data["results"][0]
                loc = top_result.get("geometry", {}).get("location", {})
                return {
                    "formatted_address": top_result.get("formatted_address"),
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng"),
                }
            return {"error": f"Geocoding failed with status: {data.get('status')}"}
    except Exception as e:
        return {"error": f"Geocoding request exception: {e}"}


def find_nearby_places(latitude: float, longitude: float, place_type: str = "gym") -> list[dict]:
    """Finds nearby places of a given type around coordinates using the Google Maps Places API (New).

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        place_type: Type of place to search for (e.g. 'gym', 'park', 'fitness_center', 'sports_complex').

    Returns:
        List of matching places with key fields: name, address, and location coordinates.
    """
    import json
    import os
    import urllib.request
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY not configured in environment."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": 5000.0,
            }
        },
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for place in data.get("places", []):
                results.append({
                    "name": place.get("displayName", {}).get("text", ""),
                    "address": place.get("formattedAddress", ""),
                    "location": place.get("location", {}),
                })
            return results
    except Exception as e:
        return [{"error": f"Places API request exception: {e}"}]


def generate_exercise_image(prompt: str, tool_context: Optional[ToolContext] = None) -> str:
    """Generates an exercise or workout illustration using the gemini-3.1-flash-lite-image model,
    saves it as a tool artifact, uploads it directly to Cloud Storage, and returns its public URL.

    Args:
        prompt: Description of the exercise or fitness item to generate an image for.
        tool_context: Optional ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL string of the uploaded Cloud Storage image.
    """
    import time
    from google import genai
    from google.genai import types
    from google.cloud import storage

    client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")

    res = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"High quality fitness illustration/photo: {prompt}",
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for part in res.candidates[0].content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            if part.inline_data.mime_type:
                mime_type = part.inline_data.mime_type
            break

    if not image_bytes:
        return "Error: No image content generated by the model."

    filename = f"exercise_{int(time.time())}.jpg"

    if tool_context:
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_ASSETS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    return f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET_NAME}/{filename}"


def generate_exercise_video(prompt: str, tool_context: Optional[ToolContext] = None) -> str:
    """Generates a short exercise demonstration video using Google's Omni model (gemini-omni-flash-preview),
    saves it as a tool artifact, uploads it directly to Cloud Storage, and returns its public URL.

    Args:
        prompt: Description of the exercise or workout routine to generate a video for (e.g. 'Demonstration of dumbbell chest press').
        tool_context: Optional ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL string of the uploaded Cloud Storage video (https://storage.googleapis.com/<bucket>/<object>).
    """
    import base64
    import time
    from google import genai
    from google.genai import types
    from google.cloud import storage

    client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="global")

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=f"A fitness enthusiast demonstrating exercise technique: {prompt}",
    )

    if not hasattr(interaction, "output_video") or not interaction.output_video or not interaction.output_video.data:
        return "Error: No video content generated by the model."

    mime_type = getattr(interaction.output_video, "mime_type", "video/mp4") or "video/mp4"
    video_bytes = base64.b64decode(interaction.output_video.data)

    filename = f"exercise_video_{int(time.time())}.mp4"

    if tool_context:
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_ASSETS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    return f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET_NAME}/{filename}"





