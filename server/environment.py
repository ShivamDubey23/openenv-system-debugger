from typing import Tuple, Dict, Any
from app.models import Observation, Action
from app.tasks.definitions import TASKS
from app.tasks.grader import grade_task  # Import our deterministic grader!

class DebuggingEnv:
    def __init__(self):
        self.reset()

    def reset(self, task_name: str = "easy_syntax_error") -> Observation:
        """Resets the environment to the specific task state."""
        self.current_task_name = task_name  # Track the current task
        self.current_directory = "/workspace"
        self.file_system = TASKS.get(task_name, TASKS["easy_syntax_error"]).copy()
        self.open_file_path = None
        self.last_output = f"Environment reset. Loaded task: {task_name}."
        self.step_count = 0
        self.max_steps = 15
        
        return self.get_observation()

    def get_observation(self) -> Observation:
        """Constructs the current observation state."""
        dir_contents = [
            path.replace(self.current_directory + "/", "") 
            for path in self.file_system.keys() 
            if path.startswith(self.current_directory)
        ]
        
        open_content = None
        if self.open_file_path and self.open_file_path in self.file_system:
            open_content = self.file_system[self.open_file_path]

        return Observation(
            current_directory=self.current_directory,
            directory_contents=dir_contents,
            last_command_output=self.last_output,
            open_file_content=open_content
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Executes the agent's action and updates the state."""
        self.step_count += 1
        reward = 0.0
        done = False
        info = {}

        if action.command == "ls":
            self.last_output = "Listed directory contents."

        elif action.command == "read_file":
            if action.file_path in self.file_system:
                self.open_file_path = action.file_path
                self.last_output = f"Opened {action.file_path}"
            else:
                self.last_output = f"Error: File {action.file_path} not found."
                reward = -0.1 

        elif action.command == "edit_file":
            if action.file_path and action.code_content:
                self.file_system[action.file_path] = action.code_content
                self.open_file_path = action.file_path
                self.last_output = f"Updated {action.file_path} successfully."
            else:
                self.last_output = "Error: Must provide file_path and code_content."
                reward = -0.1

        elif action.command == "run_tests":
            # Safely use the grader to determine if the code is fixed
            score = grade_task(self.current_task_name, self.file_system)
            if score == 1.0:
                self.last_output = "Tests PASSED! Code is fully fixed."
                reward = 1.0
                done = True
                info["success"] = True
            elif score > 0.0:
                self.last_output = "Tests FAILED. Partial progress detected."
                reward = score
            else:
                self.last_output = "Tests FAILED. Code is still buggy."

        elif action.command == "submit":
            done = True
            self.last_output = "Task submitted."
            info["success"] = False 

        else:
            self.last_output = f"Unknown command: {action.command}"
            reward = -0.1

        if self.step_count >= self.max_steps:
            done = True
            self.last_output += " | Max steps reached. Episode terminated."

        return self.get_observation(), reward, done, info

# Create a global instance of our environment
env_instance = DebuggingEnv()