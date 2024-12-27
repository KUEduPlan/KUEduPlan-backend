from pyswip import Prolog
from fastapi import FastAPI
import time

app = FastAPI()

# Initialize Prolog
prolog = Prolog()

# Define course data
def assert_courses():
    # Assert Department data
    prolog.asserta('department(1, "Engineering")')
    prolog.assertz('major(1, "Software Engineering")')
    prolog.assertz('departmentOf(1, 1)')

    # Assert RequiredCourseByMajor data
    prolog.assertz('requiredCourseByMajor(1, 101)')
    prolog.assertz('requiredCourseByMajor(1, 102)')
    prolog.assertz('requiredCourseByMajor(1, 103)')
    prolog.assertz('requiredCourseByMajor(1, 104)')
    prolog.assertz('requiredCourseByMajor(1, 105)')
    prolog.assertz('requiredCourseByMajor(1, 106)')

    # Assert Course data
    prolog.assertz('course(101, "Introduction to CS", 1, 1)')
    prolog.assertz('course(102, "Algorithms", 2, 2)')
    prolog.assertz('course(103, "Data Analysis", 1, 1)')
    prolog.assertz('course(104, "Machine Learning", 3, 2)')
    prolog.assertz('course(105, "Robotics Engineering", 2, 1)')
    prolog.assertz('course(106, "AI for Robotics", 4, 2)')

    # Assert Prerequisite data
    prolog.assertz('prerequisiteOf(101, 102)')
    prolog.assertz('corequisiteOf(101, 102)')

    prolog.assertz('prerequisiteOf(102, 105)')
    prolog.assertz('corequisiteOf(102, 105)')

    prolog.assertz('''prerequisiteOf(A, C) :-
                   prerequisiteOf(A, B),
                   prerequisiteOf(B, C)
                   ''')
    
    # Assert Student data year 2 semester 1
    prolog.assertz('student(1001, "Alice Johnson", 2023, "Bachelor", 1, 1, 1, "Active")')

    # Assert Grades and Registration data
    prolog.assertz('recievedGrade(1001, 101, "A", 2023)')
    prolog.assertz('recievedGrade(1001, 103, "B", 2023)')
    prolog.assertz('register(1001, 105, 2024, 1)')
    prolog.assertz('register(1001, 103, 2023, 1)') 
    prolog.assertz('register(1001, 101, 2023, 1)')  # Added missing registration for course 101

    # Asset current year
    prolog.assertz(f'currentYear({time.localtime().tm_year})')


    # Assert the passedCourse rule with correct course/4 references
    prolog.assertz(
        '''passedCourse(StdId, CId, RegisterYear, RegisterSem) :- 
        student(StdId, _, _, _, _, _, _, _), 
        course(CId, _, _, _),
        recievedGrade(StdId, CId, Grade, RegisterYear), 
        register(StdId, CId, RegisterYear, RegisterSem), 
        Grade \= "F"
        '''
    )

    # # Register major subject without pre, co, pre-co
    prolog.assertz(
        '''canRegister(StdId, CId, Year, StdSem) :-
        currentYear(Year),
        course(CId, _, AllowYear, OpenSem),
        student(StdId, _, StdYear, _, _, _, StdSem, _),
        StdSem == OpenSem,
        Year - StdYear >= AllowYear
        '''
    )


    # Register pre course
    prolog.assertz('''
    canRegister(StdId, CId, Year, StdSem) :-
        currentYear(Year),
        student(StdId, _, StdYear, _, _, _, StdSem, _),
        course(CId, _, AllowYear, OpenSem),
        prerequisiteOf(CID2, CId),
        CID2 \= CId,                        % Prevent circular prerequisites
        StdSem == OpenSem,                   % Course is open in the current semester
        Year - StdYear >= AllowYear,         % Student meets the year requirement
        passedCourse(StdId, CID2, RegisterYear, RegisterSem), % Prerequisite passed
        RegisterYear =< Year,                % Prerequisite was completed before this year
        RegisterSem \= StdSem          % Prerequisite was not completed this semester
    ''')

    # # Register Pre-Co
    prolog.assertz(
        '''canRegister(StdId, CId, Year, StdSem) :-
        currentYear(Year),
        student(StdId, _, StdYear, _, _, _, StdSem, _),
        course(CId, _, AllowYear, OpenSem),
        prerequisiteOf(_, CId),
        corequisiteOf(_, CId),
        StdSem == OpenSem,
        Year - StdYear >= AllowYear,
        \+ passedCourse(StdId, CId, RegisterYear, RegisterSem),
        RegisterYear =< Year,
        RegisterSem \= StdSem,
        register(StdId, _, Year, StdSem)
        '''
    )

    # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, FutureYear, RegisterSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            recievedGrade(StdId, CId, Grade, RegisterYear),
            course(CId, _, AllowYear, OpenSem),
            Grade == "Undefind",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            Year - StdYear =< AllowYear,
            register(StdId, _, Year, StdSem)
            '''
    )

        # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, FutureYear, RegisterSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            recievedGrade(StdId, CId, Grade, RegisterYear),
            course(CId, _, AllowYear, OpenSem),
            Grade == "F",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            Year - StdYear >= AllowYear,
            register(StdId, _, Year, StdSem)
            '''
    )

    

# Query for passed courses
def passed_courses():
    results = list(prolog.query("passedCourse(1001, Y, Z, M)"))
    print(results)

def register_subject():
    results = list(prolog.query("canRegister(1001, X, Y, Z)"))
    print(results)

# Main function
def main():
    assert_courses()
    passed_courses()
    register_subject()

# Run the script
if __name__ == "__main__":
    main()