import uuid
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

# Import your services (Ensure these files exist as per previous steps)
from app.services.ai_gateway import ModelGateway
from app.services.voting_engine import calculate_ranked_choice_winner

app = FastAPI(title="Pack Vote API")

# --- 1. Static Files & Frontend Routes ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')

@app.get("/vote/{trip_id}")
async def read_vote_page(trip_id: str):
    return FileResponse('app/static/vote.html')

@app.get("/results/{trip_id}")
async def read_results_page(trip_id: str):
    return FileResponse('app/static/results.html')

# --- 2. Observability ---
Instrumentator().instrument(app).expose(app)

# --- 3. Data Models (Updated to match HTML) ---
class WebTripRequest(BaseModel):
    origin: str
    vibe: str
    # Optional fields for when we add SMS later
    organizer_phone: Optional[str] = None
    participants: Optional[List[str]] = []

class VoteSubmission(BaseModel):
    ranked_preferences: List[str]  # e.g. ['PAR', 'TOK', 'CUN']

# --- 4. Dependency Injection ---
# Simple singleton pattern for the Gateway
gateway_instance = ModelGateway()
def get_gateway():
    return gateway_instance

# --- 5. API Endpoints ---

@app.post("/trips/create")
async def create_trip(
    trip: WebTripRequest, 
    background_tasks: BackgroundTasks,
    gateway: ModelGateway = Depends(get_gateway)
):
    # Generate a unique ID for this session
    trip_id = str(uuid.uuid4())[:8]
    
    # 1. AI AGENT: Validate budget/vibe (The "Thinking" Step)
    # We use a simplified context for the demo
    system_prompt = f"You are a travel agent. User is in {trip.origin}. Budget is strict."
    recommendation = await gateway.generate(
        task_type="destination_recommendation",
        context={"prefs": trip.vibe},
        provider="auto"
    )
    
    print(f"🤖 AI Recommendation for Trip {trip_id}: {recommendation}")

    # In a real app, you would save 'recommendation' to a DB here.
    
    return {
        "status": "created", 
        "trip_id": trip_id,
        "ai_comment": recommendation
    }

@app.post("/trips/{trip_id}/vote")
async def submit_vote(trip_id: str, vote: VoteSubmission):
    # In production: Save vote to Postgres/Redis
    print(f"🗳️ Vote received for {trip_id}: {vote.ranked_preferences}")
    
    # We are just logging it for now. 
    # To make the chart move, we need to save this to a global list (see below).
    MOCK_DB[trip_id].append(vote.ranked_preferences)
    
    return {"status": "accepted"}

@app.get("/trips/{trip_id}/calculate")
async def calculate_results(trip_id: str):
    # Retrieve votes from our in-memory mock DB
    ballots = MOCK_DB.get(trip_id, [])
    
    if not ballots:
        # Default mock data so the chart isn't empty on first load
        ballots = [
            ["Paris", "Tokyo", "Cancun"],
            ["Tokyo", "Paris", "Cancun"],
            ["Cancun", "Tokyo", "Paris"],
            ["Paris", "Cancun", "Tokyo"]
        ]
    
    result = calculate_ranked_choice_winner(ballots)
    return result

# --- 6. In-Memory Mock Database ---
# (Resets when server restarts - good for demos)
from collections import defaultdict
MOCK_DB = defaultdict(list)