from pyswip import Prolog
from fastapi import FastAPI
app = FastAPI()

# Initialize Prolog
prolog = Prolog()

# Define course data
def assert_courses():
    prolog.assertz("course('01219114', 'Prog 1', 1, 1, 1, [1], [], ['01219115'])")
    prolog.assertz("course('01219115', 'Prog 1 Lab', 1, 1, 1, [1], [], ['01219114'])")
    prolog.assertz("course('01219118', 'Discrete', 1, 1, 1, [1], [], [])")
    prolog.assertz("course('01417167', 'Math 1', 1, 1, 1, [1, 2, 3], [], [])")
    prolog.assertz("course('01420111', 'Physics 1', 1, 1, 1, [1, 2, 3], [], [])")
    prolog.assertz("course('01219116', 'Prog 2', 1, 2, 1, [2], ['01219114', '01219115'], ['01219117'])")
    prolog.assertz("course('01219117', 'Prog 2 Lab', 1, 2, 1, [2], ['01219114', '01219115'], ['01219116'])")
    prolog.assertz("course('01219217', 'Algo 1', 1, 2, 1, [2], ['01219118'], [])")
    prolog.assertz("course('01204216', 'Prob Stat', 1, 2, 1, [2], ['01417167'], [])")
    prolog.assertz("course('01417168', 'Math 2', 1, 2, 1, [1, 2, 3], ['01417167'], [])")
    prolog.assertz("course('01420113', 'Physics 1 Lab', 1, 2, 1, [2], [], ['01420111'])")
    prolog.assertz("course('01219212', 'Algo Lab', 2, 1, 1, [1], ['01219114', '01219115'], ['01219217'])")
    prolog.assertz("course('01219218', 'Algo 2', 2, 1, 1, [1], ['01219217'], [])")
    prolog.assertz("course('01219224', 'Network', 2, 1, 1, [1], [], [])")
    prolog.assertz("course('01219231', 'Database', 2, 1, 1, ['01219217'], [], [])")
    prolog.assertz("course('01219241', 'ISP', 2, 1, 1, ['01219116', '01219117'], [], [])")
    prolog.assertz("course('01204461', 'AI', 2, 2, 2, [], [], [])")
    prolog.assertz("course('01219222', 'ComSys', 2, 2, 2, ['01219114', '01219115'], ['01219223'], [])")
    prolog.assertz("course('01219223', 'ComSys Lab', 2, 2, 2, [], ['01219222'], [])")
    prolog.assertz("course('01219243', 'Soft Design', 2, 2, 2, ['01219116', '01219117'], [], [])")
    prolog.assertz("course('01219335', 'DAQ', 2, 2, 2, ['01219114', '01219115'], [], [])")
    prolog.assertz("course('01219343', 'Testing', 2, 2, 2, ['01219241'], [], [])")
    prolog.assertz("course('01219313', 'Comm Skill', 3, 1, 1, [], [], [])")
    prolog.assertz("course('01219325', 'Soft Security', 3, 1, 1, ['01219241'], [], [])")
    prolog.assertz("course('01219346', 'Soft Process', 3, 1, 1, ['01219241'], [], [])")
    prolog.assertz("course('01219366', 'KE', 3, 1, 1, ['01219118'], [], [])")
    prolog.assertz("course('01219367', 'Data Analytics', 3, 1, 1, ['01204216'], [], [])")
    prolog.assertz("course('01219395', 'Project Prep', 3, 2, 2, ['01219241'], [], [])")
    prolog.assertz("course('01219449', 'Soft Arch', 3, 2, 2, ['01219241'], [], [])")
    prolog.assertz("course('01219461', 'Big Data', 3, 2, 2, ['01219217'], [], [])")
    prolog.assertz("course('01219462', 'Soft AI', 3, 2, 2, ['01219241'], [], [])")
    prolog.assertz("course('01219490', 'Coop', 4, 1, 1, ['01219241', '01219243'], [], [])")
    prolog.assertz("course('01219497', 'Seminar', 4, 2, 2, [], [], [])")
    prolog.assertz("course('01219499', 'Project', 4, 2, 2, ['01219395'], [], [])")
    # Add other courses here similarly...

# Helper function to convert integers to strings
def convert_integers_to_strings(lst):
    return [str(i) if isinstance(i, int) else i for i in lst]

# Query for courses in a specific year and semester
def find_courses_by_year_semester(year, semester):
    query = f'course(ID, ShortName, {year}, {semester}, SemOpen, Pre, Co, PreCo)'
    result = list(prolog.query(query))
    return result

# Query for passed courses
def passed_courses(current_year, current_semester):
    query = f'course(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo), ' \
            f'(Year < {current_year} ; (Year = {current_year}, Semester < {current_semester}))'
    result = list(prolog.query(query))
    return result

# Query for future courses
def future_courses_to_register(current_year, current_semester):
    query = f'course(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo), ' \
            f'(Year > {current_year} ; (Year = {current_year}, Semester > {current_semester}))'
    result = list(prolog.query(query))
    return result

# Main entry point for testing
def main():
    # Assert the course data
    assert_courses()

    # Set current year and semester
    current_year = 2
    current_semester = 1

    # Find courses for the given year and semester
    current_courses = find_courses_by_year_semester(current_year, current_semester)
    print(f"Courses in Year {current_year}, Semester {current_semester}:")
    print(current_courses)

    # # Get passed courses
    passed_courses_list = passed_courses(current_year, current_semester)
    print("\nPassed courses:")
    print(passed_courses_list)

    # # Get future courses to register
    future_courses = future_courses_to_register(current_year, current_semester)
    print("\nFuture courses to register:")
    print(future_courses)


# Run the main function
if __name__ == "__main__":
    main()
