import os
from typing import Dict, Tuple, Any
from server.models import Observation, Action

class SystemDebuggingEnv:
    def __init__(self):
        self.current_task_name = "easy_syntax_error"
        self.step_count = 0
        self.max_steps = 15
        self.file_system: Dict[str, str] = {}
        self.workspace_dir = "/workspace"

    def reset(self, task_id: str) -> Observation:
        """Resets the environment for a new task."""
        self.current_task_name = task_id
        self.step_count = 0
        self.file_system = self._load_task_files(task_id)
        
        goal_msg = (
            f"Fix the bugs in {task_id}. Use 'ls' to list directory contents, "
            "'read_file' to view code, 'edit_file' to patch, 'run_tests' to verify, "
            "and 'submit' when done. All files are located in /workspace."
        )
        return Observation(
            text=f"Environment reset. Task: {task_id}\nGoal: {goal_msg}",
            last_action_error=False
        )

    def _load_task_files(self, task_id: str) -> Dict[str, str]:
        """Loads the virtual file system based on the selected task."""
        files = {}
        if task_id == "easy_syntax_error":
            files["/workspace/script.py"] = "def calculate_sum(a, b)\n    return a + b"
        elif task_id == "medium_logic_bug":
            files["/workspace/sorter.cpp"] = "#include <iostream>\n// TODO: Implement bubble sort"
        elif task_id == "hard_integration_failure":
            files["/workspace/data_processor.py"] = "import cpp_engine\n# Broken integration logic"
            files["/workspace/cpp_engine.cpp"] = "// C++ backend missing Python bindings"
        return files

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Executes one agent action and returns the next state."""
        self.step_count += 1
        cmd = action.command
        path = action.file_path
        content = action.code_content
        
        output = ""
        error = False
        done = False
        reward = 0.0
        
        # --- COMMAND LOGIC ---
        if cmd == "ls":
            output = "Listed directory contents. Files: " + ", ".join(self.file_system.keys())
            reward = 0.0
            
        elif cmd == "read_file":
            if path in self.file_system:
                output = f"Opened {path}\n{self.file_system[path]}"
                reward = 0.0
            else:
                output = f"Error: File {path} not found."
                error = True
                reward = -0.1
                
        elif cmd == "edit_file":
            if path in self.file_system and content is not None:
                self.file_system[path] = content
                output = f"Updated {path} successfully."
                reward = 0.0
            else:
                output = f"Error: File {path} not found or no content provided."
                error = True
                reward = -0.1
                
        elif cmd == "run_tests":
            # A dummy test runner that checks if files were modified
            if self.current_task_name == "medium_logic_bug" and "iostream" in self.file_system.get("/workspace/sorter.cpp", ""):
                 output = "Tests PASSED! Code is fully fixed."
                 reward = 1.0
                 done = True
            else:
                 output = "Tests FAILED."
                 error = True
                 reward = -0.1
                 
        elif cmd == "submit":
            output = "Task submitted."
            done = True
            reward = 0.0
            
        else:
            output = f"Unknown command: {cmd}"
            error = True
            reward = -0.1

        # --- ENFORCE MAX STEPS ---
        if self.step_count >= self.max_steps and not done:
            done = True
            output += " | Max steps reached. Episode terminated."

        obs = Observation(text=output, last_action_error=error)
        return obs, reward, done, {"step_count": self.step_count}

# Instantiate the global environment
env_instance = SystemDebuggingEnv()