# FitCoach AI

FitCoach AI is an intelligent, agentic fitness and workout assistant built with the **Google Agent Development Kit (ADK)** and deployed on **Google Cloud Agent Platform**. It helps users explore exercises, log workouts, calculate heart rate training zones, find nearby gyms, and generate visual exercise illustrations and demonstration videos.

![FitCoach AI Demo](demo.gif)

---

## 🚀 Key Implemented Features & Integrations

FitCoach AI integrates with native Google Cloud services and Google GenAI models:

- **🧠 Cross-Session Memory (Vertex AI Memory Bank)**: Powered by `VertexAiMemoryBankService`. Persists user health conditions, medical facts, past surgeries, chronic issues, and fitness preferences across conversations.
- **🗄️ Firestore Database Integration**: Connected to Google Cloud Firestore to query the exercise catalog (`exercises` collection) and log completed user workouts (`workout_logs` collection).
- **🪣 Google Cloud Storage Assets**: Directly uploads generated exercise illustrations and demonstration videos to a public GCS bucket (`fitcoach-ai-assets-qwiklabs-gcp-03-675a8fdff8e3`) for instant public URL delivery.
- **🎨 AI Image Generation (`gemini-3.1-flash-lite-image`)**: Tool (`generate_exercise_image`) that produces exercise illustrations, saves them as ADK artifacts, and uploads them to Cloud Storage.
- **🎬 AI Video Generation (`gemini-omni-flash-preview`)**: Tool (`generate_exercise_video`) running in the `global` region that creates exercise technique demonstration videos, saves them as ADK artifacts, and returns public GCS HTTPS URLs.
- **📊 A2UI Rich Cards (v0.8 Basic Catalog)**: Formats exercise responses into structured A2UI card surfaces (Cards, Columns, Rows, Text, Images) rendered natively in `adk web` and the custom web frontend.
- **🐍 Cloud Code Execution Sandbox (`AgentEngineSandboxCodeExecutor`)**: Runs Python code inside the Agent Platform sandbox to calculate target heart rate training zones using the Karvonen formula.
- **📍 Google Maps Geocoding & Places API**: Converts street addresses into coordinates and searches for nearby gyms and fitness centers within a 5km radius.
- **🏋️ Public Exercise Database Integration**: Connects to the Wger Workout API to search live exercise instructions and equipment requirements.

---

## 🏗️ Architecture Overview

```
[ Web Browser / Frontend UI ]
            │
            ▼
   [ FastAPI Proxy ]
            │ (A2A Protocol)
            ▼
[ Agent Engine / Reasoning Engine ]
            │
 ┌──────────┼────────────────────────────┬────────────────────────────┐
 │          │                            │                            │
 ▼          ▼                            ▼                            ▼
[ Firestore ] [ Vertex AI Memory Bank ] [ Google Cloud Storage ] [ Code Sandbox ]
```

---

## 🛠️ Local Development & Setup

### Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud` CLI) authenticated with your GCP project
- Active GCP Project with Firestore, Vertex AI, and Cloud Storage enabled

### 1. Install Agent Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```ini
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 3. Run Agent Locally with ADK

Start the local Agent Development Kit web playground:

```bash
adk web --port 8000
```

Open your browser to the local ADK playground interface to interact with the agent.

---

## 🌐 Running the Web Frontend

The custom chat web UI consists of a FastAPI proxy communicating with the agent over the A2A protocol.

### 1. Install Frontend Dependencies

```bash
pip install -r frontend/requirements.txt
```

### 2. Start the Frontend Proxy

```bash
cd frontend
AGENT_DIRECTORY="app" python main.py
```

---

## ☁️ Deployment Instructions

### Deploy Agent to Agent Platform

```bash
agents-cli deploy \
  --project YOUR_GCP_PROJECT_ID \
  --update-env-vars GOOGLE_MAPS_API_KEY=YOUR_MAPS_API_KEY
```

### Deploy Frontend to Cloud Run

```bash
gcloud run deploy fitcoach-ai-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="YOUR_AGENT_RUNTIME_RESOURCE_NAME",AGENT_DIRECTORY="app" \
  --project YOUR_GCP_PROJECT_ID
```

---

## 📄 License

Copyright 2026 Google LLC. Managed under the Apache 2.0 License.
