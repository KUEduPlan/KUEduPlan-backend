from fastapi import FastAPI, HTTPException
import subprocess
import os

app = FastAPI()

# Function to run Prolog queries
def run_prolog_query(query: str) -> str:
    """
    Runs a Prolog query using subprocess.

    Args:
        query (str): The Prolog query to execute.

    Returns:
        str: The output of the Prolog interpreter.

    Raises:
        FileNotFoundError: If the Prolog interpreter is not found.
        subprocess.SubprocessError: If the subprocess execution fails.
    """
    try:
        # Modify the command according to your Prolog interpreter
        result = subprocess.run(
            ["swipl", "-g", query, "-t", "halt"],  # Example for SWI-Prolog
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,  # Raise an exception if the command fails
        )
        return result.stdout
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Prolog interpreter not found. Is it installed and in PATH?"
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing Prolog query: {e.stderr.strip()}",
        )

# API endpoint to handle Prolog queries
@app.get("/current_courses/{department_id}/{semester_id}")
def get_current_courses(department_id: int, semester_id: int):
    """
    Endpoint to fetch current courses based on department and semester.

    Args:
        department_id (int): The department ID.
        semester_id (int): The semester ID.

    Returns:
        dict: The Prolog query result.
    """
    # Construct the Prolog query (adjust to your Prolog program logic)
    query = f"fetch_courses({department_id}, {semester_id}, Result), write(Result)."

    # Log the query for debugging
    print(f"Running Prolog query: {query}")

    # Execute the query
    output = run_prolog_query(query)

    # Parse the output or return raw output
    return {"output": output}

# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}



@app.get("/passed_courses/{year}/{semester}")
def get_passed_courses(year: int, semester: int):
    query = f"passed_courses({year}, {semester}, Result), " \
            f"convert_course_data(Result, Converted), write(Converted)."
    output = run_prolog_query(query)
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Failed to parse Prolog output", "output": output}
    return {"passed_courses": data}


@app.get("/future_courses/{year}/{semester}")
def get_future_courses(year: int, semester: int):
    query = f"future_courses_to_register({year}, {semester}, Result), " \
            f"convert_course_data(Result, Converted), write(Converted)."
    output = run_prolog_query(query)
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Failed to parse Prolog output", "output": output}
    return {"future_courses": data}
