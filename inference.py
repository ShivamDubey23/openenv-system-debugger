import os
import json
import requests
from openai import OpenAI

# --- STRICT ENVIRONMENT VARIABLE FORMATTING ---
# Matches the exact pattern required by the Hackathon checklist
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("WARNING: HF_TOKEN is missing. Make sure it is injected by the validator or set locally.")
    # Local fallback ONLY if not running in the strict validator
    HF_TOKEN = os.getenv("GROQ_API_KEY", "dummy_key") 

client = OpenAI(
    api_key=HF_TOKEN,
    base_url=API_BASE_URL 
)

API_URL = "http://127.0.0.1:8000"

def run_agent_on_task(task_name: str) -> float:
    # STRICT LOG: START
    print(f"START {task_name}")
    
    res = requests.post(f"{API_URL}/reset", json={"task_id": task_name})
    if res.status_code != 200:
        print(f"END {task_name} 0.0")
        return 0.0
        
    obs = res.json()
    done = False
    step = 0
    
    messages = [
        {"role": "system", "content": (
            "You are an autonomous AI system programmer. "
            "Output ONLY valid JSON matching this schema: "
            "{\"command\": \"ls\"|\"read_file\"|\"edit_file\"|\"run_tests\"|\"submit\", "
            "\"file_path\": \"target file\", \"code_content\": \"code to write\"}. "
            "Do not include markdown. Fix the bugs to pass the tests."
        )}
    ]

    while not done and step < 15:
        step += 1
        messages.append({"role": "user", "content": f"Current Observation: {json.dumps(obs)}"})
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME, 
                messages=messages,
                temperature=0.0,
            )
            raw_action = response.choices[0].message.content.strip()
        except Exception:
            raw_action = '{"command": "submit"}'
            
        # STRICT LOG: STEP
        print(f"STEP {step} {raw_action}")
        messages.append({"role": "assistant", "content": raw_action})
        
        try:
            action_dict = json.loads(raw_action)
        except json.JSONDecodeError:
            action_dict = {"command": "submit"}
        
        step_res = requests.post(f"{API_URL}/step", json=action_dict)
        if step_res.status_code != 200:
            break
            
        step_data = step_res.json()
        obs = step_data["observation"]
        done = step_data["done"]

    # Get final score
    grader_res = requests.get(f"{API_URL}/grader", params={"task_name": task_name})
    score = float(grader_res.json().get("score", 0.0))
    
    # STRICT LOG: END
    print(f"END {task_name} {score}")
    return score

if __name__ == "__main__":
    tasks = ["easy_syntax_error", "medium_logic_bug", "hard_integration_failure"]
    final_scores = {}
    
    for task in tasks:
        final_scores[task] = run_agent_on_task(task)