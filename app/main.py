from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from app.tasks.grader import grade_task
from fastapi import Request

# Import the strict OpenEnv schemas
from app.models import Observation, Action, Reward

# IMPORT YOUR LIVE ENVIRONMENT HERE
from app.environment import env_instance

app = FastAPI(title="Meta OpenEnv - System Debugging Environment")

# The spec requires step() to return observation, reward, done, and info.
class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

@app.post("/step", response_model=StepResponse)
async def step(action: Action):
    # 1. Feed the agent's action into the live environment
    obs, reward, done, info = env_instance.step(action)
    
    # 2. Return the results matching the OpenEnv spec
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info=info
    )

@app.post("/reset", response_model=Observation)
async def reset(request: Request):
    """Bulletproof reset endpoint that handles both query params and JSON bodies."""
    task_name = "easy_syntax_error"
    
    # 1. Check if the bot sent it as a query parameter
    if "task_name" in request.query_params:
        task_name = request.query_params["task_name"]
        
    # 2. Check if the bot sent it inside a JSON POST body
    try:
        body = await request.json()
        if isinstance(body, dict) and "task_name" in body:
            task_name = body["task_name"]
    except Exception:
        pass # No JSON body was provided, which is fine
        
    return env_instance.reset(task_name)

@app.get("/state", response_model=Observation)
async def state():
    # Return what the agent currently sees without taking a step
    return env_instance.get_observation()

# --- ADDITIONAL ENDPOINTS REQUIRED BY THE HACKATHON CHECKLIST ---

@app.get("/tasks")
async def get_tasks():
    return {
        "tasks": ["easy_syntax_error", "medium_logic_bug", "hard_integration_failure"],
        "action_schema": Action.model_json_schema()
    }

@app.get("/grader")
async def get_grader(task_name: str = "easy_syntax_error"):
    # Calculate the score based on the environment's current file system
    final_score = grade_task(task_name, env_instance.file_system)
    return {"score": final_score}

@app.post("/baseline")
async def run_baseline():
    # Placeholder: We will write the baseline inference script later
    return {
        "baseline_scores": {
            "easy_syntax_error": 0.0, 
            "medium_logic_bug": 0.0, 
            "hard_integration_failure": 0.0
        }
    }