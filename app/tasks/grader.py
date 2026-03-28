from typing import Dict

def grade_task(task_name: str, file_system: Dict[str, str]) -> float:
    """
    Deterministically grades the agent's performance based on the final file system state.
    Returns a float between 0.0 and 1.0.
    """
    score = 0.0

    if task_name == "easy_syntax_error":
        content = file_system.get("/workspace/calculator.py", "")
        # Optimal fix: added the parenthesis
        if "print(add(5, 3))" in content:
            score = 1.0
        # Partial/Hack fix: just deleted the broken line to make it compile
        elif "print(" not in content: 
            score = 0.5
            
    elif task_name == "medium_logic_bug":
        content = file_system.get("/workspace/sorter.cpp", "")
        # Optimal fix: flipped the comparison operator to ascending
        if "if(arr[i] > arr[j])" in content:
            score = 1.0

    elif task_name == "hard_integration_failure":
        py_content = file_system.get("/workspace/data_processor.py", "")
        cpp_content = file_system.get("/workspace/cpp_engine.cpp", "")
        
        # Did the agent make C++ output valid JSON?
        cpp_is_json = '{"status": "success"}' in cpp_content.replace(" ", "")
        # Did the agent change Python to parse plain text instead of JSON?
        py_is_text = "json.loads" not in py_content
        
        if cpp_is_json and "json.loads" in py_content:
            score = 1.0 # Optimal: Fixed the C++ backend
        elif py_is_text and "status: success" in cpp_content:
            score = 1.0 # Alternative: Adapted the Python frontend
        elif cpp_is_json or py_is_text:
            score = 0.5 # Partial: Changed one file, but they still don't match
            
    return score