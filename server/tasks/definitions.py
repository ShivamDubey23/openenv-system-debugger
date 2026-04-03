from typing import Dict

# EASY: A simple syntax error in a Python script
EASY_TASK: Dict[str, str] = {
    "/workspace/calculator.py": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\n# Bug: Missing closing parenthesis\nprint(add(5, 3)",
    "/workspace/tests/test_calc.py": "from calculator import add, subtract\n\ndef test_math():\n    assert add(2, 2) == 4\n    assert subtract(5, 2) == 3\n"
}

# MEDIUM: A logic bug in a C++ sorting algorithm
MEDIUM_TASK: Dict[str, str] = {
    "/workspace/sorter.cpp": "#include <iostream>\n#include <vector>\n\nstd::vector<int> sort_array(std::vector<int> arr) {\n    for(int i=0; i<arr.size(); i++) {\n        for(int j=i+1; j<arr.size(); j++) {\n            // Bug: Wrong comparison operator (sorts descending instead of ascending)\n            if(arr[i] < arr[j]) {\n                std::swap(arr[i], arr[j]);\n            }\n        }\n    }\n    return arr;\n}\n",
    "/workspace/tests/test_sorter.py": "import subprocess\n# Test script checks if output is strictly ascending\n"
}

# HARD: Integration failure between Python and C++
HARD_TASK: Dict[str, str] = {
    "/workspace/data_processor.py": "import subprocess\nimport json\n\ndef process_data():\n    # Bug: expects JSON, but C++ engine outputs plain text\n    result = subprocess.run(['./cpp_engine'], capture_output=True, text=True)\n    data = json.loads(result.stdout)\n    return data['status']\n",
    "/workspace/cpp_engine.cpp": "#include <iostream>\n\nint main() {\n    // Bug: Outputting plain text instead of JSON format expected by Python\n    std::cout << \"status: success\" << std::endl;\n    return 0;\n}\n"
}

# Export the tasks so the environment can load them
TASKS = {
    "easy_syntax_error": EASY_TASK,
    "medium_logic_bug": MEDIUM_TASK,
    "hard_integration_failure": HARD_TASK
}