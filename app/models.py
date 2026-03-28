from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class Observation(BaseModel):
    """What the AI agent 'sees' at each step."""
    current_directory: str = Field(description="The current working directory.")
    directory_contents: List[str] = Field(description="List of files and folders in the current directory.")
    last_command_output: str = Field(description="Standard output or error from the last executed action.")
    open_file_content: Optional[str] = Field(default=None, description="Content of the currently opened file, if any.")

class Action(BaseModel):
    """The commands the AI agent can execute."""
    command: str = Field(description="The action to take: 'ls', 'read_file', 'edit_file', 'run_tests', or 'submit'.")
    file_path: Optional[str] = Field(default=None, description="Target file path for read or edit commands.")
    code_content: Optional[str] = Field(default=None, description="Code to insert or replace when editing a file.")

class Reward(BaseModel):
    """The feedback returned to the agent after an action."""
    score: float = Field(ge=0.0, le=1.0, description="Partial progress score from 0.0 to 1.0.")
    is_done: bool = Field(description="True if the task is fully completed or permanently failed.")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional context or error messages.")