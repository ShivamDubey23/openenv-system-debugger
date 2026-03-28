# OpenEnv: System Debugging & Refactoring Environment

## Environment Description & Motivation
This environment simulates a realistic backend software engineering workflow. AI agents are placed in a virtual workspace containing a mix of Python and C++ source code. The agent must navigate the file system, read broken code, identify bugs (ranging from simple syntax errors to complex cross-language integration failures), edit the files, and run tests to verify their fixes.

**Real-World Utility (Motivation):**
Most coding benchmarks evaluate an LLM's ability to generate code from scratch in a single turn. However, real-world software engineering consists of navigating legacy codebases, debugging existing logic, and ensuring components in different languages communicate correctly. This environment tests an agent's multi-step reasoning, file navigation, and debugging capabilities in a realistic setting.

---

## Action and Observation Spaces

The environment strictly adheres to the OpenEnv Pydantic specification.

### Observation Space
At each step, the agent receives:
* `current_directory` (str): The present working directory.
* `directory_contents` (List[str]): Files and folders visible in the current directory.
* `last_command_output` (str): stdout/stderr from the previous action (crucial for test results).
* `open_file_content` (str | None): The source code of the currently inspected file.

### Action Space
The agent can execute the following commands via the `command` string:
* `ls`: Lists the contents of the current directory.
* `read_file`: Opens a file (requires `file_path`).
* `edit_file`: Modifies a file (requires `file_path` and `code_content`).
* `run_tests`: Executes the deterministic test suite to check for success.
* `submit`: Terminates the episode and requests final grading.

---

## Task Descriptions & Expected Difficulty

The environment features 3 deterministic tasks, graded from 0.0 to 1.0 based on the final file system state.

1. **Easy: Syntax Error (`easy_syntax_error`)**
   * *Objective:* Fix a missing closing parenthesis in a Python calculator script.
   * *Grader:* Checks for the exact syntactical fix. Partial reward (0.5) is given if the agent deletes the broken line instead of fixing it properly.

2. **Medium: Logic Bug (`medium_logic_bug`)**
   * *Objective:* A C++ sorting algorithm is sorting in descending order instead of ascending.
   * *Grader:* Parses the C++ file to ensure the comparison operator has been corrected. 

3. **Hard: Integration Failure (`hard_integration_failure`)**
   * *Objective:* A Python script expects a JSON payload from a C++ executable, but the C++ code outputs plain text.
   * *Grader:* The agent can either rewrite the C++ code to output valid JSON, or rewrite the Python code to parse plain text. Full score (1.0) for fixing the pipeline; partial score (0.5) if only one side of the integration is modified.

---

## Setup and Usage Instructions

### Running via Docker (Recommended)
This environment is containerized and ready for Hugging Face Spaces.
```bash
docker build -t openenv-debugging .
docker run -p 7860:7860 openenv-debugging