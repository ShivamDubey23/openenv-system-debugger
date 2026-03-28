import os
import json
import requests
from openai import OpenAI

# 1. Use Groq API Key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("WARNING: GROQ_API_KEY environment variable not set.")

# 2. Redirect the OpenAI client to Groq's free endpoint
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1" 
)

API_URL = "http://127.0.0.1:8000"

def run_agent_on_task(task_name: str) -> float:
    print(f"\n{'='*40}\nStarting Task: {task_name}\n{'='*40}")
    
    # Reset the environment for the specific task
    res = requests.post(f"{API_URL}/reset", params={"task_name": task_name})
    obs = res.json()
    
    done = False
    step = 0
    
    # Set up the strict system instructions for the LLM
    messages = [
        {"role": "system", "content": (
            "You are an autonomous AI system programmer. "
            "You must output ONLY valid JSON matching this schema exactly: "
            "{\"command\": \"ls\"|\"read_file\"|\"edit_file\"|\"run_tests\"|\"submit\", "
            "\"file_path\": \"optional target file\", \"code_content\": \"optional code to write\"}. "
            "Do not include markdown formatting like ```json. Fix the bugs to pass the tests."
        )}
    ]

    # The REAL Agent Loop 
    while not done and step < 15:
        step += 1
        messages.append({"role": "user", "content": f"Current Observation: {json.dumps(obs)}"})
        
       # Call Groq's Llama model
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # <--- CHANGE THIS LINE
                messages=messages,
                temperature=0.0,
            )
            raw_action = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {e}")
            raw_action = '{"command": "submit"}' # Fallback if API fails
            
        print(f"\n[Step {step}] Agent Action: {raw_action}")
        messages.append({"role": "assistant", "content": raw_action})
        
        # Parse the JSON action
        try:
            action_dict = json.loads(raw_action)
        except json.JSONDecodeError:
            print("  -> Agent failed to output valid JSON. Forcing 'submit' command.")
            action_dict = {"command": "submit"}
        
        # Send action to our OpenEnv /step API
        step_res = requests.post(f"{API_URL}/step", json=action_dict)
        step_data = step_res.json()
        
        obs = step_data["observation"]
        done = step_data["done"]
        print(f"  -> Reward: {step_data['reward']} | Done: {done}")
        print(f"  -> Output: {obs['last_command_output']}")

    # Get final deterministic score from the grader
    grader_res = requests.get(f"{API_URL}/grader", params={"task_name": task_name})
    score = grader_res.json().get("score", 0.0)
    print(f"\n*** Final Score for {task_name}: {score} ***\n")
    return score

if __name__ == "__main__":
    tasks = ["easy_syntax_error", "medium_logic_bug", "hard_integration_failure"]
    final_scores = {}
    
    # Run the agent against all 3 tasks
    for task in tasks:
        final_scores[task] = run_agent_on_task(task)
    
    print("\n" + "="*40)
    print("BASELINE EVALUATION COMPLETE")
    print(json.dumps(final_scores, indent=2))
    print("="*40)