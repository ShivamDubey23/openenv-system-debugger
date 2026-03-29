from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.models import Observation, Action
from app.environment import env_instance
from app.tasks.grader import grade_task

app = FastAPI(title="Meta OpenEnv - System Debugging Environment")

# --- OPENENV COMPLIANT SCHEMAS ---
class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    seed: Optional[int] = None

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

class StateResponse(BaseModel):
    episode_id: str
    step_count: int
    max_steps: int

# --- ENDPOINTS ---
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Environment is running"}

@app.post("/reset", response_model=Observation)
async def reset(
    task_id: Optional[str] = Query(None),
    seed: Optional[int] = Query(None),
    req: Optional[ResetRequest] = None
):
    # 1. Safely extract task_id whether it was sent in the URL or the JSON body
    target_task = task_id
    if req and req.task_id:
        target_task = req.task_id
        
    if not target_task:
        target_task = "easy_syntax_error"

    # 2. Map the bot's shorthand test names to your actual task names
    if target_task == "easy": 
        target_task = "easy_syntax_error"
    elif target_task == "medium": 
        target_task = "medium_logic_bug"
    elif target_task == "hard": 
        target_task = "hard_integration_failure"

    return env_instance.reset(target_task)

@app.post("/step", response_model=StepResponse)
async def step(action: Action):
    obs, reward, done, info = env_instance.step(action)
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info=info
    )

@app.get("/state", response_model=StateResponse)
async def get_state():
    return StateResponse(
        episode_id=getattr(env_instance, "current_task_name", "easy_syntax_error"),
        step_count=getattr(env_instance, "step_count", 0),
        max_steps=getattr(env_instance, "max_steps", 15)
    )

@app.get("/grader")
async def grader(task_name: str = "easy_syntax_error"):
    # Ensure the grader also understands shorthand
    if task_name == "easy": task_name = "easy_syntax_error"
    elif task_name == "medium": task_name = "medium_logic_bug"
    elif task_name == "hard": task_name = "hard_integration_failure"
    
    return {"score": grade_task(task_name, env_instance.file_system)}